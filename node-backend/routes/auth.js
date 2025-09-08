const express = require('express');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const { generateToken, protect, authRateLimit, checkAccountLockout } = require('../middleware/auth');

const router = express.Router();

// Validation middleware
const registerValidation = [
  body('username')
    .trim()
    .isLength({ min: 3, max: 30 })
    .withMessage('Username must be between 3 and 30 characters')
    .matches(/^[a-zA-Z0-9_-]+$/)
    .withMessage('Username can only contain letters, numbers, hyphens, and underscores'),
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, and one number')
];

const loginValidation = [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
  body('password')
    .notEmpty()
    .withMessage('Password is required')
];

const profileValidation = [
  body('profile.firstName')
    .optional()
    .trim()
    .isLength({ max: 50 })
    .withMessage('First name cannot exceed 50 characters'),
  body('profile.lastName')
    .optional()
    .trim()
    .isLength({ max: 50 })
    .withMessage('Last name cannot exceed 50 characters'),
  body('profile.age')
    .optional()
    .isInt({ min: 13, max: 120 })
    .withMessage('Age must be between 13 and 120'),
  body('profile.height')
    .optional()
    .isFloat({ min: 50, max: 300 })
    .withMessage('Height must be between 50 and 300 cm'),
  body('profile.weight')
    .optional()
    .isFloat({ min: 20, max: 500 })
    .withMessage('Weight must be between 20 and 500 kg')
];

// @desc    Register new user
// @route   POST /api/auth/register
// @access  Public
router.post('/register', registerValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { username, email, password, profile = {} } = req.body;

    // Check if user already exists
    const existingUser = await User.findOne({
      $or: [
        { email: email.toLowerCase() },
        { username: username.toLowerCase() }
      ]
    });

    if (existingUser) {
      if (existingUser.email === email.toLowerCase()) {
        return res.status(400).json({
          success: false,
          message: 'Email already registered'
        });
      } else {
        return res.status(400).json({
          success: false,
          message: 'Username already taken'
        });
      }
    }

    // Create user
    const user = await User.create({
      username: username.toLowerCase(),
      email: email.toLowerCase(),
      password,
      profile: {
        ...profile,
        firstName: profile.firstName?.trim(),
        lastName: profile.lastName?.trim()
      }
    });

    // Generate token
    const token = generateToken(user._id);

    // Set session
    req.session.userId = user._id;
    req.session.save();

    res.status(201).json({
      success: true,
      message: 'User registered successfully',
      data: {
        user: {
          id: user._id,
          username: user.username,
          email: user.email,
          profile: user.profile,
          role: user.role,
          statistics: user.statistics
        },
        token
      }
    });

  } catch (error) {
    console.error('Registration error:', error);
    
    if (error.code === 11000) {
      const field = Object.keys(error.keyPattern)[0];
      return res.status(400).json({
        success: false,
        message: `${field} already exists`
      });
    }

    res.status(500).json({
      success: false,
      message: 'Server error during registration'
    });
  }
});

// @desc    Login user
// @route   POST /api/auth/login
// @access  Public
router.post('/login', 
  authRateLimit(5, 15 * 60 * 1000),
  checkAccountLockout,
  loginValidation,
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          success: false,
          message: 'Validation failed',
          errors: errors.array()
        });
      }

      const { email, password } = req.body;

      // Check for user
      const user = await User.findOne({ email: email.toLowerCase() }).select('+password');

      if (!user) {
        return res.status(401).json({
          success: false,
          message: 'Invalid credentials'
        });
      }

      // Check account status
      if (!user.isActive) {
        return res.status(401).json({
          success: false,
          message: 'Account is deactivated'
        });
      }

      // Check password
      const isMatch = await user.matchPassword(password);

      if (!isMatch) {
        // Increment login attempts
        await user.incLoginAttempts();
        
        return res.status(401).json({
          success: false,
          message: 'Invalid credentials'
        });
      }

      // Reset login attempts on successful login
      if (user.loginAttempts > 0) {
        await user.updateOne({
          $unset: {
            loginAttempts: 1,
            lockUntil: 1
          },
          $set: {
            lastLogin: new Date()
          }
        });
      } else {
        user.lastLogin = new Date();
        await user.save();
      }

      // Generate token
      const token = generateToken(user._id);

      // Set session
      req.session.userId = user._id;
      req.session.save();

      // Remove password from response
      user.password = undefined;

      res.json({
        success: true,
        message: 'Login successful',
        data: {
          user: {
            id: user._id,
            username: user.username,
            email: user.email,
            profile: user.profile,
            role: user.role,
            statistics: user.statistics,
            lastLogin: user.lastLogin
          },
          token
        }
      });

    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({
        success: false,
        message: 'Server error during login'
      });
    }
  }
);

// @desc    Logout user
// @route   POST /api/auth/logout
// @access  Private
router.post('/logout', protect, (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      console.error('Session destruction error:', err);
      return res.status(500).json({
        success: false,
        message: 'Logout failed'
      });
    }

    res.clearCookie('connect.sid');
    res.json({
      success: true,
      message: 'Logged out successfully'
    });
  });
});

// @desc    Get current user profile
// @route   GET /api/auth/profile
// @access  Private
router.get('/profile', protect, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      data: {
        user: {
          id: user._id,
          username: user.username,
          email: user.email,
          profile: user.profile,
          role: user.role,
          statistics: user.statistics,
          preferences: user.profile.preferences,
          goals: user.profile.goals,
          performanceMetrics: user.getPerformanceMetrics(),
          createdAt: user.createdAt
        }
      }
    });

  } catch (error) {
    console.error('Profile fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch profile'
    });
  }
});

// @desc    Update user profile
// @route   PUT /api/auth/profile
// @access  Private
router.put('/profile', protect, profileValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const allowedUpdates = ['profile', 'preferences'];
    const updates = {};

    // Build update object
    Object.keys(req.body).forEach(key => {
      if (allowedUpdates.includes(key)) {
        if (key === 'profile') {
          updates.profile = { ...req.user.profile.toObject(), ...req.body.profile };
        } else {
          updates[key] = req.body[key];
        }
      }
    });

    const user = await User.findByIdAndUpdate(
      req.user.id,
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
      message: 'Profile updated successfully',
      data: {
        user: {
          id: user._id,
          username: user.username,
          email: user.email,
          profile: user.profile,
          performanceMetrics: user.getPerformanceMetrics()
        }
      }
    });

  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update profile'
    });
  }
});

// @desc    Add fitness goal
// @route   POST /api/auth/goals
// @access  Private
router.post('/goals', protect, [
  body('type')
    .isIn(['weight_loss', 'muscle_gain', 'endurance', 'strength', 'general_fitness'])
    .withMessage('Invalid goal type'),
  body('target')
    .isNumeric()
    .withMessage('Target must be a number'),
  body('deadline')
    .optional()
    .isISO8601()
    .withMessage('Invalid date format')
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

    const { type, target, deadline } = req.body;

    const user = await User.findById(req.user.id);
    
    // Check if goal type already exists and is active
    const existingGoal = user.profile.goals.find(
      goal => goal.type === type && !goal.achieved
    );

    if (existingGoal) {
      return res.status(400).json({
        success: false,
        message: 'You already have an active goal of this type'
      });
    }

    user.profile.goals.push({
      type,
      target,
      deadline: deadline ? new Date(deadline) : undefined
    });

    await user.save();

    res.status(201).json({
      success: true,
      message: 'Goal added successfully',
      data: {
        goals: user.profile.goals
      }
    });

  } catch (error) {
    console.error('Goal creation error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to add goal'
    });
  }
});

// @desc    Update fitness goal
// @route   PUT /api/auth/goals/:goalId
// @access  Private
router.put('/goals/:goalId', protect, async (req, res) => {
  try {
    const { goalId } = req.params;
    const { achieved, target } = req.body;

    const user = await User.findById(req.user.id);
    const goal = user.profile.goals.id(goalId);

    if (!goal) {
      return res.status(404).json({
        success: false,
        message: 'Goal not found'
      });
    }

    if (achieved !== undefined) goal.achieved = achieved;
    if (target !== undefined) goal.target = target;

    await user.save();

    res.json({
      success: true,
      message: 'Goal updated successfully',
      data: {
        goal
      }
    });

  } catch (error) {
    console.error('Goal update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update goal'
    });
  }
});

// @desc    Verify authentication status
// @route   GET /api/auth/verify
// @access  Private
router.get('/verify', protect, (req, res) => {
  res.json({
    success: true,
    message: 'Token is valid',
    data: {
      user: {
        id: req.user._id,
        username: req.user.username,
        email: req.user.email,
        role: req.user.role
      }
    }
  });
});

module.exports = router;