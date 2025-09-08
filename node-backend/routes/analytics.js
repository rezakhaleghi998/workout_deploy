const express = require('express');
const { query, validationResult } = require('express-validator');
const Workout = require('../models/Workout');
const User = require('../models/User');
const { protect, optionalAuth } = require('../middleware/auth');

const router = express.Router();

// @desc    Get user workout analytics
// @route   GET /api/analytics/workouts
// @access  Private
router.get('/workouts', protect, [
  query('startDate').optional().isISO8601().withMessage('Invalid start date format'),
  query('endDate').optional().isISO8601().withMessage('Invalid end date format'),
  query('period').optional().isIn(['week', 'month', 'quarter', 'year']).withMessage('Invalid period')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    let { startDate, endDate, period = 'month' } = req.query;

    // Set default date range based on period
    if (!startDate || !endDate) {
      const now = new Date();
      endDate = now.toISOString();

      switch (period) {
        case 'week':
          startDate = new Date(now.setDate(now.getDate() - 7)).toISOString();
          break;
        case 'quarter':
          startDate = new Date(now.setMonth(now.getMonth() - 3)).toISOString();
          break;
        case 'year':
          startDate = new Date(now.setFullYear(now.getFullYear() - 1)).toISOString();
          break;
        case 'month':
        default:
          startDate = new Date(now.setMonth(now.getMonth() - 1)).toISOString();
      }
    }

    // Get workout analytics
    const analytics = await Workout.getAnalytics(req.user.id, startDate, endDate);
    
    // Get daily breakdown
    const dailyStats = await Workout.aggregate([
      {
        $match: {
          user: req.user._id,
          date: { $gte: new Date(startDate), $lte: new Date(endDate) }
        }
      },
      {
        $group: {
          _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
          workouts: { $sum: 1 },
          totalCalories: { $sum: "$totalCalories" },
          totalDuration: { $sum: "$totalDuration" },
          avgIntensity: {
            $avg: {
              $switch: {
                branches: [
                  { case: { $eq: ["$overallIntensity", "low"] }, then: 1 },
                  { case: { $eq: ["$overallIntensity", "moderate"] }, then: 2 },
                  { case: { $eq: ["$overallIntensity", "high"] }, then: 3 },
                  { case: { $eq: ["$overallIntensity", "extreme"] }, then: 4 }
                ],
                default: 2
              }
            }
          }
        }
      },
      { $sort: { _id: 1 } }
    ]);

    // Get workout type distribution
    const typeDistribution = await Workout.aggregate([
      {
        $match: {
          user: req.user._id,
          date: { $gte: new Date(startDate), $lte: new Date(endDate) }
        }
      },
      {
        $group: {
          _id: "$type",
          count: { $sum: 1 },
          totalCalories: { $sum: "$totalCalories" },
          totalDuration: { $sum: "$totalDuration" }
        }
      },
      { $sort: { count: -1 } }
    ]);

    // Get intensity distribution
    const intensityDistribution = await Workout.aggregate([
      {
        $match: {
          user: req.user._id,
          date: { $gte: new Date(startDate), $lte: new Date(endDate) }
        }
      },
      {
        $group: {
          _id: "$overallIntensity",
          count: { $sum: 1 }
        }
      }
    ]);

    // Calculate streaks and patterns
    const allWorkouts = await Workout.find({
      user: req.user.id,
      date: { $gte: new Date(startDate), $lte: new Date(endDate) }
    }).select('date').sort({ date: 1 });

    // Calculate current streak
    let currentStreak = 0;
    let longestStreak = 0;
    let tempStreak = 0;
    let lastDate = null;

    allWorkouts.forEach(workout => {
      const workoutDate = new Date(workout.date).toDateString();
      
      if (lastDate) {
        const daysDiff = (new Date(workoutDate) - new Date(lastDate)) / (1000 * 60 * 60 * 24);
        
        if (daysDiff === 1) {
          tempStreak += 1;
        } else if (daysDiff > 1) {
          longestStreak = Math.max(longestStreak, tempStreak);
          tempStreak = 1;
        }
      } else {
        tempStreak = 1;
      }
      
      lastDate = workoutDate;
    });

    longestStreak = Math.max(longestStreak, tempStreak);
    
    // Check if current streak is active (last workout within 2 days)
    if (allWorkouts.length > 0) {
      const lastWorkout = allWorkouts[allWorkouts.length - 1];
      const daysSinceLastWorkout = (Date.now() - new Date(lastWorkout.date)) / (1000 * 60 * 60 * 24);
      currentStreak = daysSinceLastWorkout <= 2 ? tempStreak : 0;
    }

    // Get performance trends
    const performanceTrend = await Workout.aggregate([
      {
        $match: {
          user: req.user._id,
          date: { $gte: new Date(startDate), $lte: new Date(endDate) }
        }
      },
      {
        $group: {
          _id: {
            week: { $week: "$date" },
            year: { $year: "$date" }
          },
          avgCaloriesPerWorkout: { $avg: "$totalCalories" },
          avgDuration: { $avg: "$totalDuration" },
          workoutCount: { $sum: 1 }
        }
      },
      { $sort: { "_id.year": 1, "_id.week": 1 } }
    ]);

    res.json({
      success: true,
      data: {
        period,
        dateRange: { startDate, endDate },
        summary: analytics[0] || {
          totalWorkouts: 0,
          totalCalories: 0,
          totalDuration: 0,
          averageCalories: 0,
          averageDuration: 0,
          workoutTypeBreakdown: {}
        },
        dailyStats,
        typeDistribution,
        intensityDistribution,
        streaks: {
          current: currentStreak,
          longest: longestStreak
        },
        performanceTrend,
        insights: generateInsights(analytics[0], typeDistribution, intensityDistribution, currentStreak)
      }
    });

  } catch (error) {
    console.error('Workout analytics error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch workout analytics'
    });
  }
});

// @desc    Get performance metrics
// @route   GET /api/analytics/performance
// @access  Private
router.get('/performance', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    
    // Calculate performance metrics
    const performanceMetrics = user.getPerformanceMetrics();
    
    // Get recent performance trend (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const recentWorkouts = await Workout.find({
      user: req.user.id,
      date: { $gte: thirtyDaysAgo }
    }).sort({ date: 1 });

    // Calculate weekly performance
    const weeklyPerformance = [];
    const weeks = 4;
    
    for (let i = weeks - 1; i >= 0; i--) {
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - (i * 7) - 7);
      const weekEnd = new Date();
      weekEnd.setDate(weekEnd.getDate() - (i * 7));

      const weekWorkouts = recentWorkouts.filter(w => 
        w.date >= weekStart && w.date < weekEnd
      );

      weeklyPerformance.push({
        week: `Week ${weeks - i}`,
        startDate: weekStart,
        endDate: weekEnd,
        workouts: weekWorkouts.length,
        totalCalories: weekWorkouts.reduce((sum, w) => sum + w.totalCalories, 0),
        totalDuration: weekWorkouts.reduce((sum, w) => sum + w.totalDuration, 0),
        averageIntensity: weekWorkouts.length > 0 ? 
          weekWorkouts.reduce((sum, w) => {
            const intensityMap = { low: 1, moderate: 2, high: 3, extreme: 4 };
            return sum + intensityMap[w.overallIntensity];
          }, 0) / weekWorkouts.length : 0
      });
    }

    // Calculate fitness score (0-100)
    const fitnessScore = calculateFitnessScore(performanceMetrics, weeklyPerformance);

    // Get comparison with other users (percentile)
    const allUsersStats = await User.aggregate([
      { $match: { isActive: true } },
      {
        $project: {
          totalCalories: '$statistics.totalCaloriesBurned',
          totalWorkouts: '$statistics.totalWorkouts',
          averageWorkoutsPerWeek: {
            $divide: [
              { $multiply: ['$statistics.totalWorkouts', 7] },
              {
                $divide: [
                  { $subtract: [new Date(), '$statistics.joinDate'] },
                  1000 * 60 * 60 * 24
                ]
              }
            ]
          }
        }
      }
    ]);

    const userPercentiles = calculatePercentiles(performanceMetrics, allUsersStats);

    res.json({
      success: true,
      data: {
        performanceMetrics,
        fitnessScore,
        weeklyPerformance,
        percentiles: userPercentiles,
        recommendations: generatePerformanceRecommendations(performanceMetrics, weeklyPerformance, fitnessScore)
      }
    });

  } catch (error) {
    console.error('Performance analytics error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch performance analytics'
    });
  }
});

// @desc    Get global platform statistics
// @route   GET /api/analytics/platform
// @access  Public
router.get('/platform', optionalAuth, async (req, res) => {
  try {
    // Platform-wide statistics
    const totalUsers = await User.countDocuments({ isActive: true });
    const totalWorkouts = await Workout.countDocuments();
    
    const platformStats = await Workout.aggregate([
      {
        $group: {
          _id: null,
          totalCaloriesBurned: { $sum: '$totalCalories' },
          totalDuration: { $sum: '$totalDuration' },
          averageWorkoutDuration: { $avg: '$totalDuration' },
          averageCaloriesPerWorkout: { $avg: '$totalCalories' }
        }
      }
    ]);

    // Most popular workout types
    const popularWorkoutTypes = await Workout.aggregate([
      {
        $group: {
          _id: '$type',
          count: { $sum: 1 },
          avgCalories: { $avg: '$totalCalories' },
          avgDuration: { $avg: '$totalDuration' }
        }
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]);

    // Recent activity (last 7 days)
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);

    const recentActivity = await Workout.aggregate([
      { $match: { date: { $gte: weekAgo } } },
      {
        $group: {
          _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
          workouts: { $sum: 1 },
          calories: { $sum: "$totalCalories" }
        }
      },
      { $sort: { _id: 1 } }
    ]);

    // Top performers (public leaderboard)
    const topPerformers = await User.find({ isActive: true })
      .select('username profile.firstName statistics.totalCaloriesBurned statistics.totalWorkouts')
      .sort({ 'statistics.totalCaloriesBurned': -1 })
      .limit(5);

    res.json({
      success: true,
      data: {
        platform: {
          totalUsers,
          totalWorkouts,
          totalCaloriesBurned: platformStats[0]?.totalCaloriesBurned || 0,
          totalDuration: platformStats[0]?.totalDuration || 0,
          averageWorkoutDuration: Math.round(platformStats[0]?.averageWorkoutDuration || 0),
          averageCaloriesPerWorkout: Math.round(platformStats[0]?.averageCaloriesPerWorkout || 0)
        },
        popularWorkoutTypes: popularWorkoutTypes.map(type => ({
          name: type._id,
          count: type.count,
          avgCalories: Math.round(type.avgCalories),
          avgDuration: Math.round(type.avgDuration)
        })),
        recentActivity,
        topPerformers: topPerformers.map((user, index) => ({
          rank: index + 1,
          name: user.profile.firstName || user.username,
          username: user.username,
          totalCalories: user.statistics.totalCaloriesBurned,
          totalWorkouts: user.statistics.totalWorkouts
        }))
      }
    });

  } catch (error) {
    console.error('Platform analytics error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch platform analytics'
    });
  }
});

// Helper function to generate insights
function generateInsights(summary, typeDistribution, intensityDistribution, currentStreak) {
  const insights = [];

  if (summary) {
    // Workout frequency insights
    if (summary.totalWorkouts === 0) {
      insights.push({
        type: 'motivation',
        message: 'Start your fitness journey today! Log your first workout.',
        priority: 'high'
      });
    } else if (summary.totalWorkouts < 5) {
      insights.push({
        type: 'consistency',
        message: 'Great start! Try to maintain consistency with 3-4 workouts per week.',
        priority: 'medium'
      });
    }

    // Calorie insights
    if (summary.averageCalories < 200) {
      insights.push({
        type: 'intensity',
        message: 'Consider increasing workout intensity to burn more calories.',
        priority: 'medium'
      });
    } else if (summary.averageCalories > 500) {
      insights.push({
        type: 'achievement',
        message: 'Excellent calorie burn rate! Keep up the high-intensity workouts.',
        priority: 'low'
      });
    }

    // Duration insights
    if (summary.averageDuration < 20) {
      insights.push({
        type: 'duration',
        message: 'Try extending workouts to 30-45 minutes for optimal benefits.',
        priority: 'medium'
      });
    }
  }

  // Streak insights
  if (currentStreak === 0) {
    insights.push({
      type: 'streak',
      message: 'Build momentum! Start a new workout streak today.',
      priority: 'high'
    });
  } else if (currentStreak >= 7) {
    insights.push({
      type: 'achievement',
      message: `Amazing ${currentStreak}-day streak! You're on fire! 🔥`,
      priority: 'low'
    });
  }

  // Variety insights
  if (typeDistribution.length === 1) {
    insights.push({
      type: 'variety',
      message: 'Add variety to your routine with different workout types.',
      priority: 'medium'
    });
  }

  return insights;
}

// Helper function to calculate fitness score
function calculateFitnessScore(metrics, weeklyPerformance) {
  let score = 0;

  // Base score from total metrics
  score += Math.min(30, metrics.totalWorkouts * 0.5);
  score += Math.min(20, metrics.totalCaloriesBurned / 1000);
  score += Math.min(15, metrics.longestStreak * 2);

  // Consistency score from weekly performance
  const activeWeeks = weeklyPerformance.filter(week => week.workouts > 0).length;
  score += activeWeeks * 5;

  // Recent activity boost
  const lastWeekWorkouts = weeklyPerformance[weeklyPerformance.length - 1]?.workouts || 0;
  score += Math.min(10, lastWeekWorkouts * 2);

  return Math.min(100, Math.round(score));
}

// Helper function to calculate user percentiles
function calculatePercentiles(userMetrics, allUsersStats) {
  const calculatePercentile = (value, allValues) => {
    const sorted = allValues.sort((a, b) => a - b);
    const index = sorted.findIndex(v => v >= value);
    return index === -1 ? 100 : Math.round((index / sorted.length) * 100);
  };

  return {
    totalCalories: calculatePercentile(
      userMetrics.totalCaloriesBurned,
      allUsersStats.map(u => u.totalCalories).filter(v => v > 0)
    ),
    totalWorkouts: calculatePercentile(
      userMetrics.totalWorkouts,
      allUsersStats.map(u => u.totalWorkouts).filter(v => v > 0)
    ),
    averageWorkoutsPerWeek: calculatePercentile(
      userMetrics.averageWorkoutsPerWeek,
      allUsersStats.map(u => u.averageWorkoutsPerWeek).filter(v => v > 0)
    )
  };
}

// Helper function to generate performance recommendations
function generatePerformanceRecommendations(metrics, weeklyPerformance, fitnessScore) {
  const recommendations = [];

  if (fitnessScore < 30) {
    recommendations.push({
      category: 'consistency',
      title: 'Build Workout Consistency',
      description: 'Aim for 3-4 workouts per week to establish a routine',
      priority: 'high'
    });
  }

  if (metrics.averageWorkoutDuration < 25) {
    recommendations.push({
      category: 'duration',
      title: 'Extend Workout Duration',
      description: 'Gradually increase workout time to 30-45 minutes',
      priority: 'medium'
    });
  }

  const lastTwoWeeks = weeklyPerformance.slice(-2);
  const workoutDecline = lastTwoWeeks.length === 2 && 
    lastTwoWeeks[1].workouts < lastTwoWeeks[0].workouts;

  if (workoutDecline) {
    recommendations.push({
      category: 'motivation',
      title: 'Maintain Momentum',
      description: 'Your workout frequency has decreased. Try to get back on track!',
      priority: 'high'
    });
  }

  if (metrics.longestStreak < 7) {
    recommendations.push({
      category: 'streak',
      title: 'Build a Weekly Streak',
      description: 'Challenge yourself to workout for 7 consecutive days',
      priority: 'medium'
    });
  }

  return recommendations;
}

module.exports = router;