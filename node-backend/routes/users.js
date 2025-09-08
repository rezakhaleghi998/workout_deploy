const express = require('express');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const Workout = require('../models/Workout');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// @desc    Get user statistics
// @route   GET /api/users/stats
// @access  Private
router.get('/stats', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const performanceMetrics = user.getPerformanceMetrics();
    
    // Get recent workouts
    const recentWorkouts = await Workout.getUserHistory(req.user.id, 5);
    
    // Get weekly stats
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    
    const weeklyWorkouts = await Workout.find({
      user: req.user.id,
      date: { $gte: weekAgo }
    });

    const weeklyStats = {
      workoutCount: weeklyWorkouts.length,
      totalCalories: weeklyWorkouts.reduce((sum, w) => sum + w.totalCalories, 0),
      totalDuration: weeklyWorkouts.reduce((sum, w) => sum + w.totalDuration, 0),
      averageIntensity: weeklyWorkouts.length > 0 ? 
        weeklyWorkouts.reduce((sum, w) => {
          const intensityMap = { low: 1, moderate: 2, high: 3, extreme: 4 };
          return sum + intensityMap[w.overallIntensity];
        }, 0) / weeklyWorkouts.length : 0
    };

    res.json({
      success: true,
      data: {
        userStats: performanceMetrics,
        weeklyStats,
        recentWorkouts: recentWorkouts.map(w => w.getSummary()),
        goals: user.profile.goals,
        preferences: user.profile.preferences
      }
    });

  } catch (error) {
    console.error('User stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch user statistics'
    });
  }
});

// @desc    Get leaderboard
// @route   GET /api/users/leaderboard
// @access  Public
router.get('/leaderboard', async (req, res) => {
  try {
    const { limit = 10, type = 'calories' } = req.query;
    
    let sortField;
    switch (type) {
      case 'workouts':
        sortField = 'statistics.totalWorkouts';
        break;
      case 'streak':
        sortField = 'statistics.longestStreak';
        break;
      case 'calories':
      default:
        sortField = 'statistics.totalCaloriesBurned';
    }

    const leaders = await User.find({ 
      isActive: true,
      [`${sortField}`]: { $gt: 0 }
    })
    .select(`username profile.firstName profile.lastName statistics.totalWorkouts 
             statistics.totalCaloriesBurned statistics.longestStreak statistics.joinDate`)
    .sort({ [sortField]: -1 })
    .limit(parseInt(limit));

    const leaderboard = leaders.map((user, index) => ({
      rank: index + 1,
      username: user.username,
      name: user.profile.fullName || user.username,
      totalWorkouts: user.statistics.totalWorkouts,
      totalCalories: user.statistics.totalCaloriesBurned,
      longestStreak: user.statistics.longestStreak,
      memberSince: user.statistics.joinDate,
      score: user.statistics[sortField.split('.')[1]]
    }));

    res.json({
      success: true,
      data: {
        leaderboard,
        type,
        total: leaders.length
      }
    });

  } catch (error) {
    console.error('Leaderboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch leaderboard'
    });
  }
});

// @desc    Get user public profile
// @route   GET /api/users/:userId/profile
// @access  Public
router.get('/:userId/profile', async (req, res) => {
  try {
    const { userId } = req.params;
    
    const user = await User.findById(userId)
      .select('username profile.firstName profile.lastName profile.fitnessLevel 
               statistics.totalWorkouts statistics.totalCaloriesBurned 
               statistics.longestStreak statistics.joinDate')
      .where('isActive', true);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Get recent workouts (public summary only)
    const recentWorkouts = await Workout.find({ user: userId })
      .select('name type totalCalories totalDuration date overallIntensity')
      .sort({ date: -1 })
      .limit(5);

    res.json({
      success: true,
      data: {
        user: {
          id: user._id,
          username: user.username,
          name: user.profile.fullName || user.username,
          fitnessLevel: user.profile.fitnessLevel,
          memberSince: user.statistics.joinDate,
          stats: {
            totalWorkouts: user.statistics.totalWorkouts,
            totalCalories: user.statistics.totalCaloriesBurned,
            longestStreak: user.statistics.longestStreak
          }
        },
        recentWorkouts: recentWorkouts.map(w => ({
          id: w._id,
          name: w.name,
          type: w.type,
          calories: w.totalCalories,
          duration: w.totalDuration,
          intensity: w.overallIntensity,
          date: w.date
        }))
      }
    });

  } catch (error) {
    console.error('Public profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch user profile'
    });
  }
});

// @desc    Search users
// @route   GET /api/users/search
// @access  Private
router.get('/search', protect, async (req, res) => {
  try {
    const { q, limit = 10 } = req.query;
    
    if (!q || q.trim().length < 2) {
      return res.status(400).json({
        success: false,
        message: 'Search query must be at least 2 characters'
      });
    }

    const searchRegex = new RegExp(q, 'i');
    
    const users = await User.find({
      $and: [
        { isActive: true },
        { _id: { $ne: req.user.id } },
        {
          $or: [
            { username: searchRegex },
            { 'profile.firstName': searchRegex },
            { 'profile.lastName': searchRegex },
            { email: searchRegex }
          ]
        }
      ]
    })
    .select('username profile.firstName profile.lastName profile.fitnessLevel statistics.totalWorkouts')
    .limit(parseInt(limit));

    res.json({
      success: true,
      data: {
        users: users.map(user => ({
          id: user._id,
          username: user.username,
          name: user.profile.fullName || user.username,
          fitnessLevel: user.profile.fitnessLevel,
          totalWorkouts: user.statistics.totalWorkouts
        })),
        query: q,
        count: users.length
      }
    });

  } catch (error) {
    console.error('User search error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to search users'
    });
  }
});

// @desc    Get user achievements
// @route   GET /api/users/achievements
// @access  Private
router.get('/achievements', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id);
    
    const achievements = [];
    
    // Workout count milestones
    const workoutMilestones = [1, 5, 10, 25, 50, 100, 250, 500, 1000];
    workoutMilestones.forEach(milestone => {
      if (user.statistics.totalWorkouts >= milestone) {
        achievements.push({
          id: `workouts_${milestone}`,
          title: `${milestone} Workout${milestone > 1 ? 's' : ''}`,
          description: `Completed ${milestone} workout${milestone > 1 ? 's' : ''}`,
          category: 'workouts',
          earned: true,
          earnedDate: user.statistics.joinDate // Approximate
        });
      }
    });

    // Calorie milestones
    const calorieMilestones = [500, 1000, 5000, 10000, 25000, 50000, 100000];
    calorieMilestones.forEach(milestone => {
      if (user.statistics.totalCaloriesBurned >= milestone) {
        achievements.push({
          id: `calories_${milestone}`,
          title: `${milestone.toLocaleString()} Calories Burned`,
          description: `Burned ${milestone.toLocaleString()} total calories`,
          category: 'calories',
          earned: true,
          earnedDate: user.statistics.joinDate
        });
      }
    });

    // Streak milestones
    const streakMilestones = [3, 7, 14, 30, 60, 90, 180, 365];
    streakMilestones.forEach(milestone => {
      if (user.statistics.longestStreak >= milestone) {
        achievements.push({
          id: `streak_${milestone}`,
          title: `${milestone} Day Streak`,
          description: `Maintained a ${milestone} day workout streak`,
          category: 'streak',
          earned: true,
          earnedDate: user.statistics.joinDate
        });
      }
    });

    // Goal completion achievements
    const completedGoals = user.profile.goals.filter(goal => goal.achieved);
    if (completedGoals.length > 0) {
      achievements.push({
        id: 'goal_achiever',
        title: 'Goal Achiever',
        description: `Completed ${completedGoals.length} fitness goal${completedGoals.length > 1 ? 's' : ''}`,
        category: 'goals',
        earned: true,
        earnedDate: completedGoals[0].createdAt
      });
    }

    // Time-based achievements
    const daysSinceMember = Math.floor((Date.now() - user.statistics.joinDate) / (1000 * 60 * 60 * 24));
    const timeMilestones = [30, 90, 180, 365, 730];
    timeMilestones.forEach(days => {
      if (daysSinceMember >= days) {
        achievements.push({
          id: `member_${days}`,
          title: `${days} Day Member`,
          description: `Been a member for ${days} days`,
          category: 'membership',
          earned: true,
          earnedDate: new Date(user.statistics.joinDate.getTime() + (days * 24 * 60 * 60 * 1000))
        });
      }
    });

    // Sort by category and date
    achievements.sort((a, b) => {
      if (a.category !== b.category) {
        return a.category.localeCompare(b.category);
      }
      return new Date(b.earnedDate) - new Date(a.earnedDate);
    });

    res.json({
      success: true,
      data: {
        achievements,
        summary: {
          total: achievements.length,
          categories: {
            workouts: achievements.filter(a => a.category === 'workouts').length,
            calories: achievements.filter(a => a.category === 'calories').length,
            streak: achievements.filter(a => a.category === 'streak').length,
            goals: achievements.filter(a => a.category === 'goals').length,
            membership: achievements.filter(a => a.category === 'membership').length
          }
        }
      }
    });

  } catch (error) {
    console.error('Achievements error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch achievements'
    });
  }
});

// @desc    Update user preferences
// @route   PUT /api/users/preferences
// @access  Private
router.put('/preferences', protect, [
  body('units.weight').optional().isIn(['kg', 'lbs']),
  body('units.height').optional().isIn(['cm', 'ft']),
  body('units.distance').optional().isIn(['km', 'miles']),
  body('notifications.workoutReminders').optional().isBoolean(),
  body('notifications.goalDeadlines').optional().isBoolean(),
  body('notifications.weeklyReports').optional().isBoolean()
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

    const user = await User.findById(req.user.id);
    
    // Update preferences
    if (req.body.units) {
      user.profile.preferences.units = {
        ...user.profile.preferences.units,
        ...req.body.units
      };
    }

    if (req.body.notifications) {
      user.profile.preferences.notifications = {
        ...user.profile.preferences.notifications,
        ...req.body.notifications
      };
    }

    await user.save();

    res.json({
      success: true,
      message: 'Preferences updated successfully',
      data: {
        preferences: user.profile.preferences
      }
    });

  } catch (error) {
    console.error('Preferences update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update preferences'
    });
  }
});

module.exports = router;