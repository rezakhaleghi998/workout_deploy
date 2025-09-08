const express = require('express');
const { body, query, validationResult } = require('express-validator');
const User = require('../models/User');
const Workout = require('../models/Workout');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// Apply authentication and admin authorization to all admin routes
router.use(protect);
router.use(authorize('admin', 'moderator'));

// @desc    Get admin dashboard statistics
// @route   GET /api/admin/dashboard
// @access  Private (Admin)
router.get('/dashboard', async (req, res) => {
  try {
    // User statistics
    const totalUsers = await User.countDocuments();
    const activeUsers = await User.countDocuments({ isActive: true });
    const newUsersThisMonth = await User.countDocuments({
      createdAt: { $gte: new Date(new Date().setDate(1)) }
    });

    // Workout statistics
    const totalWorkouts = await Workout.countDocuments();
    const workoutsThisMonth = await Workout.countDocuments({
      date: { $gte: new Date(new Date().setDate(1)) }
    });

    // Platform metrics
    const platformMetrics = await Workout.aggregate([
      {
        $group: {
          _id: null,
          totalCaloriesBurned: { $sum: '$totalCalories' },
          totalDurationMinutes: { $sum: '$totalDuration' },
          averageWorkoutDuration: { $avg: '$totalDuration' },
          averageCaloriesPerWorkout: { $avg: '$totalCalories' }
        }
      }
    ]);

    // User engagement metrics
    const userEngagement = await User.aggregate([
      { $match: { isActive: true } },
      {
        $group: {
          _id: null,
          avgWorkoutsPerUser: { $avg: '$statistics.totalWorkouts' },
          avgCaloriesPerUser: { $avg: '$statistics.totalCaloriesBurned' },
          avgStreakLength: { $avg: '$statistics.longestStreak' }
        }
      }
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
          uniqueUsers: { $addToSet: "$user" },
          calories: { $sum: "$totalCalories" }
        }
      },
      {
        $addFields: {
          uniqueUserCount: { $size: "$uniqueUsers" }
        }
      },
      {
        $project: {
          uniqueUsers: 0
        }
      },
      { $sort: { _id: 1 } }
    ]);

    // Popular workout types
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
      { $limit: 5 }
    ]);

    // Top performing users
    const topUsers = await User.find({ isActive: true })
      .select('username email profile.firstName profile.lastName statistics createdAt lastLogin')
      .sort({ 'statistics.totalCaloriesBurned': -1 })
      .limit(10);

    // User registration trend (last 30 days)
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const registrationTrend = await User.aggregate([
      { $match: { createdAt: { $gte: thirtyDaysAgo } } },
      {
        $group: {
          _id: { $dateToString: { format: "%Y-%m-%d", date: "$createdAt" } },
          registrations: { $sum: 1 }
        }
      },
      { $sort: { _id: 1 } }
    ]);

    res.json({
      success: true,
      data: {
        overview: {
          totalUsers,
          activeUsers,
          inactiveUsers: totalUsers - activeUsers,
          newUsersThisMonth,
          totalWorkouts,
          workoutsThisMonth,
          ...platformMetrics[0],
          ...userEngagement[0]
        },
        recentActivity,
        popularWorkoutTypes: popularWorkoutTypes.map(type => ({
          ...type,
          avgCalories: Math.round(type.avgCalories),
          avgDuration: Math.round(type.avgDuration)
        })),
        topUsers: topUsers.map((user, index) => ({
          rank: index + 1,
          id: user._id,
          username: user.username,
          email: user.email,
          name: user.profile.firstName && user.profile.lastName ? 
            `${user.profile.firstName} ${user.profile.lastName}` : null,
          stats: user.statistics,
          memberSince: user.createdAt,
          lastLogin: user.lastLogin
        })),
        registrationTrend
      }
    });

  } catch (error) {
    console.error('Admin dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch dashboard data'
    });
  }
});

// @desc    Get all users with pagination and filtering
// @route   GET /api/admin/users
// @access  Private (Admin)
router.get('/users', [
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('search').optional().isLength({ min: 2 }).withMessage('Search term must be at least 2 characters'),
  query('status').optional().isIn(['all', 'active', 'inactive']).withMessage('Invalid status filter'),
  query('role').optional().isIn(['all', 'user', 'admin', 'moderator']).withMessage('Invalid role filter'),
  query('sortBy').optional().isIn(['createdAt', 'lastLogin', 'totalWorkouts', 'totalCalories', 'username']).withMessage('Invalid sort field'),
  query('order').optional().isIn(['asc', 'desc']).withMessage('Invalid sort order')
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

    const {
      page = 1,
      limit = 20,
      search,
      status = 'all',
      role = 'all',
      sortBy = 'createdAt',
      order = 'desc'
    } = req.query;

    const skip = (parseInt(page) - 1) * parseInt(limit);

    // Build filter
    const filter = {};
    
    if (status !== 'all') {
      filter.isActive = status === 'active';
    }
    
    if (role !== 'all') {
      filter.role = role;
    }
    
    if (search) {
      const searchRegex = new RegExp(search, 'i');
      filter.$or = [
        { username: searchRegex },
        { email: searchRegex },
        { 'profile.firstName': searchRegex },
        { 'profile.lastName': searchRegex }
      ];
    }

    // Build sort
    const sortField = sortBy === 'totalWorkouts' ? 'statistics.totalWorkouts' :
                     sortBy === 'totalCalories' ? 'statistics.totalCaloriesBurned' :
                     sortBy;
    const sortOrder = order === 'asc' ? 1 : -1;

    // Get users with pagination
    const users = await User.find(filter)
      .select('-password -emailVerificationToken -passwordResetToken')
      .sort({ [sortField]: sortOrder })
      .limit(parseInt(limit))
      .skip(skip);

    // Get total count for pagination
    const totalCount = await User.countDocuments(filter);
    const totalPages = Math.ceil(totalCount / parseInt(limit));

    res.json({
      success: true,
      data: {
        users: users.map(user => ({
          id: user._id,
          username: user.username,
          email: user.email,
          profile: user.profile,
          role: user.role,
          isActive: user.isActive,
          emailVerified: user.emailVerified,
          statistics: user.statistics,
          createdAt: user.createdAt,
          updatedAt: user.updatedAt,
          lastLogin: user.lastLogin
        })),
        pagination: {
          currentPage: parseInt(page),
          totalPages,
          totalCount,
          limit: parseInt(limit),
          hasNextPage: page < totalPages,
          hasPrevPage: page > 1
        },
        filters: { search, status, role, sortBy, order }
      }
    });

  } catch (error) {
    console.error('Admin users fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch users'
    });
  }
});

// @desc    Get single user details
// @route   GET /api/admin/users/:id
// @access  Private (Admin)
router.get('/users/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-password');

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Get user's workout summary
    const workoutSummary = await Workout.aggregate([
      { $match: { user: user._id } },
      {
        $group: {
          _id: null,
          totalWorkouts: { $sum: 1 },
          totalCalories: { $sum: '$totalCalories' },
          totalDuration: { $sum: '$totalDuration' },
          avgCalories: { $avg: '$totalCalories' },
          avgDuration: { $avg: '$totalDuration' },
          workoutTypes: { $addToSet: '$type' },
          lastWorkout: { $max: '$date' }
        }
      }
    ]);

    // Get recent workouts
    const recentWorkouts = await Workout.find({ user: user._id })
      .select('name type totalCalories totalDuration date overallIntensity')
      .sort({ date: -1 })
      .limit(10);

    res.json({
      success: true,
      data: {
        user: {
          ...user.toObject(),
          performanceMetrics: user.getPerformanceMetrics()
        },
        workoutSummary: workoutSummary[0] || {
          totalWorkouts: 0,
          totalCalories: 0,
          totalDuration: 0,
          avgCalories: 0,
          avgDuration: 0,
          workoutTypes: [],
          lastWorkout: null
        },
        recentWorkouts
      }
    });

  } catch (error) {
    console.error('Admin user detail error:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        success: false,
        message: 'Invalid user ID'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to fetch user details'
    });
  }
});

// @desc    Update user
// @route   PUT /api/admin/users/:id
// @access  Private (Admin)
router.put('/users/:id', [
  body('username').optional().trim().isLength({ min: 3, max: 30 }),
  body('email').optional().isEmail().normalizeEmail(),
  body('role').optional().isIn(['user', 'admin', 'moderator']),
  body('isActive').optional().isBoolean(),
  body('emailVerified').optional().isBoolean()
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

    const allowedUpdates = ['username', 'email', 'role', 'isActive', 'emailVerified', 'profile'];
    const updates = {};

    Object.keys(req.body).forEach(key => {
      if (allowedUpdates.includes(key)) {
        updates[key] = req.body[key];
      }
    });

    // Prevent admin from deactivating themselves
    if (req.params.id === req.user.id.toString() && updates.isActive === false) {
      return res.status(400).json({
        success: false,
        message: 'Cannot deactivate your own account'
      });
    }

    // Prevent admin from changing their own role (unless they're a super admin)
    if (req.params.id === req.user.id.toString() && updates.role && req.user.role !== 'super_admin') {
      return res.status(400).json({
        success: false,
        message: 'Cannot change your own role'
      });
    }

    const user = await User.findByIdAndUpdate(
      req.params.id,
      updates,
      { new: true, runValidators: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      message: 'User updated successfully',
      data: {
        user
      }
    });

  } catch (error) {
    console.error('Admin user update error:', error);
    
    if (error.code === 11000) {
      const field = Object.keys(error.keyPattern)[0];
      return res.status(400).json({
        success: false,
        message: `${field} already exists`
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to update user'
    });
  }
});

// @desc    Delete user
// @route   DELETE /api/admin/users/:id
// @access  Private (Admin)
router.delete('/users/:id', async (req, res) => {
  try {
    // Prevent admin from deleting themselves
    if (req.params.id === req.user.id.toString()) {
      return res.status(400).json({
        success: false,
        message: 'Cannot delete your own account'
      });
    }

    const user = await User.findByIdAndDelete(req.params.id);

    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Also delete all user's workouts
    await Workout.deleteMany({ user: req.params.id });

    res.json({
      success: true,
      message: 'User and all associated data deleted successfully'
    });

  } catch (error) {
    console.error('Admin user deletion error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete user'
    });
  }
});

// @desc    Get all workouts with admin filtering
// @route   GET /api/admin/workouts
// @access  Private (Admin)
router.get('/workouts', [
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('userId').optional().isMongoId(),
  query('type').optional().isIn(['cardio', 'strength', 'mixed', 'flexibility', 'sports', 'other']),
  query('startDate').optional().isISO8601(),
  query('endDate').optional().isISO8601()
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

    const {
      page = 1,
      limit = 20,
      userId,
      type,
      startDate,
      endDate,
      sortBy = 'date',
      order = 'desc'
    } = req.query;

    const skip = (parseInt(page) - 1) * parseInt(limit);

    // Build filter
    const filter = {};
    
    if (userId) filter.user = userId;
    if (type) filter.type = type;
    
    if (startDate || endDate) {
      filter.date = {};
      if (startDate) filter.date.$gte = new Date(startDate);
      if (endDate) filter.date.$lte = new Date(endDate);
    }

    // Get workouts with user population
    const workouts = await Workout.find(filter)
      .populate('user', 'username email profile.firstName profile.lastName')
      .sort({ [sortBy]: order === 'desc' ? -1 : 1 })
      .limit(parseInt(limit))
      .skip(skip);

    const totalCount = await Workout.countDocuments(filter);
    const totalPages = Math.ceil(totalCount / parseInt(limit));

    res.json({
      success: true,
      data: {
        workouts: workouts.map(workout => ({
          ...workout.toObject(),
          user: {
            id: workout.user._id,
            username: workout.user.username,
            email: workout.user.email,
            name: workout.user.profile.firstName && workout.user.profile.lastName ?
              `${workout.user.profile.firstName} ${workout.user.profile.lastName}` : null
          }
        })),
        pagination: {
          currentPage: parseInt(page),
          totalPages,
          totalCount,
          limit: parseInt(limit),
          hasNextPage: page < totalPages,
          hasPrevPage: page > 1
        },
        filters: { userId, type, startDate, endDate, sortBy, order }
      }
    });

  } catch (error) {
    console.error('Admin workouts fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch workouts'
    });
  }
});

// @desc    Delete workout
// @route   DELETE /api/admin/workouts/:id
// @access  Private (Admin)
router.delete('/workouts/:id', async (req, res) => {
  try {
    const workout = await Workout.findByIdAndDelete(req.params.id);

    if (!workout) {
      return res.status(404).json({
        success: false,
        message: 'Workout not found'
      });
    }

    res.json({
      success: true,
      message: 'Workout deleted successfully'
    });

  } catch (error) {
    console.error('Admin workout deletion error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete workout'
    });
  }
});

// @desc    Get system statistics
// @route   GET /api/admin/system
// @access  Private (Admin)
router.get('/system', async (req, res) => {
  try {
    // Database statistics
    const dbStats = {
      users: await User.countDocuments(),
      activeUsers: await User.countDocuments({ isActive: true }),
      workouts: await Workout.countDocuments(),
      totalCalories: await Workout.aggregate([
        { $group: { _id: null, total: { $sum: '$totalCalories' } } }
      ]).then(result => result[0]?.total || 0),
      totalDuration: await Workout.aggregate([
        { $group: { _id: null, total: { $sum: '$totalDuration' } } }
      ]).then(result => result[0]?.total || 0)
    };

    // System health
    const systemHealth = {
      status: 'healthy',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    };

    res.json({
      success: true,
      data: {
        database: dbStats,
        system: systemHealth
      }
    });

  } catch (error) {
    console.error('Admin system stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch system statistics'
    });
  }
});

module.exports = router;