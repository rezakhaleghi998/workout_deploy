const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Workout = require('../models/Workout');
const { protect, optionalAuth } = require('../middleware/auth');

const router = express.Router();

// Exercise validation
const exerciseValidation = [
  body('exercises.*.name')
    .notEmpty()
    .withMessage('Exercise name is required')
    .trim(),
  body('exercises.*.category')
    .isIn(['cardio', 'strength', 'flexibility', 'sports', 'other'])
    .withMessage('Invalid exercise category'),
  body('exercises.*.duration')
    .isInt({ min: 1 })
    .withMessage('Duration must be at least 1 minute'),
  body('exercises.*.calories')
    .isFloat({ min: 0 })
    .withMessage('Calories must be a positive number'),
  body('exercises.*.intensity')
    .optional()
    .isIn(['low', 'moderate', 'high', 'extreme'])
    .withMessage('Invalid intensity level')
];

// Workout validation
const workoutValidation = [
  body('name')
    .notEmpty()
    .withMessage('Workout name is required')
    .trim()
    .isLength({ max: 100 })
    .withMessage('Workout name cannot exceed 100 characters'),
  body('type')
    .isIn(['cardio', 'strength', 'mixed', 'flexibility', 'sports', 'other'])
    .withMessage('Invalid workout type'),
  body('exercises')
    .isArray({ min: 1 })
    .withMessage('At least one exercise is required'),
  ...exerciseValidation,
  body('notes')
    .optional()
    .isLength({ max: 1000 })
    .withMessage('Notes cannot exceed 1000 characters')
];

// @desc    Create a new workout
// @route   POST /api/workouts
// @access  Private
router.post('/', protect, workoutValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const workoutData = {
      ...req.body,
      user: req.user.id
    };

    const workout = await Workout.create(workoutData);
    
    res.status(201).json({
      success: true,
      message: 'Workout created successfully',
      data: {
        workout: workout.getSummary()
      }
    });

  } catch (error) {
    console.error('Workout creation error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create workout'
    });
  }
});

// @desc    Get user's workouts
// @route   GET /api/workouts
// @access  Private
router.get('/', protect, [
  query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('Limit must be between 1 and 100'),
  query('page').optional().isInt({ min: 1 }).withMessage('Page must be a positive integer'),
  query('type').optional().isIn(['cardio', 'strength', 'mixed', 'flexibility', 'sports', 'other']),
  query('startDate').optional().isISO8601().withMessage('Invalid start date format'),
  query('endDate').optional().isISO8601().withMessage('Invalid end date format')
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

    const { limit = 10, page = 1, type, startDate, endDate, sort = '-date' } = req.query;
    const skip = (parseInt(page) - 1) * parseInt(limit);

    // Build filter
    const filter = { user: req.user.id };
    
    if (type) filter.type = type;
    
    if (startDate || endDate) {
      filter.date = {};
      if (startDate) filter.date.$gte = new Date(startDate);
      if (endDate) filter.date.$lte = new Date(endDate);
    }

    // Get workouts with pagination
    const workouts = await Workout.find(filter)
      .sort(sort)
      .limit(parseInt(limit))
      .skip(skip);

    // Get total count for pagination
    const totalCount = await Workout.countDocuments(filter);
    const totalPages = Math.ceil(totalCount / parseInt(limit));

    res.json({
      success: true,
      data: {
        workouts: workouts.map(w => w.getSummary()),
        pagination: {
          currentPage: parseInt(page),
          totalPages,
          totalCount,
          limit: parseInt(limit),
          hasNextPage: page < totalPages,
          hasPrevPage: page > 1
        },
        filters: { type, startDate, endDate, sort }
      }
    });

  } catch (error) {
    console.error('Workouts fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch workouts'
    });
  }
});

// @desc    Get single workout
// @route   GET /api/workouts/:id
// @access  Private
router.get('/:id', protect, async (req, res) => {
  try {
    const workout = await Workout.findOne({
      _id: req.params.id,
      user: req.user.id
    });

    if (!workout) {
      return res.status(404).json({
        success: false,
        message: 'Workout not found'
      });
    }

    res.json({
      success: true,
      data: {
        workout
      }
    });

  } catch (error) {
    console.error('Workout fetch error:', error);
    
    if (error.name === 'CastError') {
      return res.status(400).json({
        success: false,
        message: 'Invalid workout ID'
      });
    }

    res.status(500).json({
      success: false,
      message: 'Failed to fetch workout'
    });
  }
});

// @desc    Update workout
// @route   PUT /api/workouts/:id
// @access  Private
router.put('/:id', protect, workoutValidation, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const workout = await Workout.findOneAndUpdate(
      { _id: req.params.id, user: req.user.id },
      req.body,
      { new: true, runValidators: true }
    );

    if (!workout) {
      return res.status(404).json({
        success: false,
        message: 'Workout not found'
      });
    }

    res.json({
      success: true,
      message: 'Workout updated successfully',
      data: {
        workout: workout.getSummary()
      }
    });

  } catch (error) {
    console.error('Workout update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update workout'
    });
  }
});

// @desc    Delete workout
// @route   DELETE /api/workouts/:id
// @access  Private
router.delete('/:id', protect, async (req, res) => {
  try {
    const workout = await Workout.findOneAndDelete({
      _id: req.params.id,
      user: req.user.id
    });

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
    console.error('Workout deletion error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete workout'
    });
  }
});

// @desc    Get workout templates
// @route   GET /api/workouts/templates
// @access  Private
router.get('/templates/list', protect, async (req, res) => {
  try {
    const templates = await Workout.find({
      user: req.user.id,
      isTemplate: true
    }).select('name type exercises totalDuration totalCalories templateName createdAt');

    res.json({
      success: true,
      data: {
        templates
      }
    });

  } catch (error) {
    console.error('Templates fetch error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch workout templates'
    });
  }
});

// @desc    Create workout from template
// @route   POST /api/workouts/templates/:id/use
// @access  Private
router.post('/templates/:id/use', protect, async (req, res) => {
  try {
    const template = await Workout.findOne({
      _id: req.params.id,
      user: req.user.id,
      isTemplate: true
    });

    if (!template) {
      return res.status(404).json({
        success: false,
        message: 'Template not found'
      });
    }

    // Create new workout from template
    const workoutData = {
      name: req.body.name || template.name,
      type: template.type,
      exercises: template.exercises,
      notes: req.body.notes || template.notes,
      user: req.user.id,
      isTemplate: false
    };

    const workout = await Workout.create(workoutData);

    res.status(201).json({
      success: true,
      message: 'Workout created from template',
      data: {
        workout: workout.getSummary()
      }
    });

  } catch (error) {
    console.error('Template usage error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create workout from template'
    });
  }
});

// @desc    Save workout as template
// @route   POST /api/workouts/:id/save-template
// @access  Private
router.post('/:id/save-template', protect, [
  body('templateName')
    .notEmpty()
    .withMessage('Template name is required')
    .trim()
    .isLength({ max: 100 })
    .withMessage('Template name cannot exceed 100 characters')
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

    const workout = await Workout.findOne({
      _id: req.params.id,
      user: req.user.id
    });

    if (!workout) {
      return res.status(404).json({
        success: false,
        message: 'Workout not found'
      });
    }

    // Create template from workout
    const templateData = {
      name: req.body.templateName,
      type: workout.type,
      exercises: workout.exercises,
      notes: workout.notes,
      user: req.user.id,
      isTemplate: true,
      templateName: req.body.templateName
    };

    const template = await Workout.create(templateData);

    res.status(201).json({
      success: true,
      message: 'Workout saved as template',
      data: {
        template: {
          id: template._id,
          name: template.name,
          templateName: template.templateName,
          type: template.type,
          exerciseCount: template.exercises.length,
          createdAt: template.createdAt
        }
      }
    });

  } catch (error) {
    console.error('Template save error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to save workout as template'
    });
  }
});

// @desc    Get popular exercises
// @route   GET /api/workouts/exercises/popular
// @access  Public
router.get('/exercises/popular', optionalAuth, async (req, res) => {
  try {
    const { limit = 20 } = req.query;

    const popularExercises = await Workout.getPopularExercises(parseInt(limit));

    res.json({
      success: true,
      data: {
        exercises: popularExercises.map(exercise => ({
          name: exercise._id,
          category: exercise.category,
          timesPerformed: exercise.count,
          averageCalories: Math.round(exercise.averageCalories * 10) / 10,
          averageDuration: Math.round(exercise.averageDuration * 10) / 10
        }))
      }
    });

  } catch (error) {
    console.error('Popular exercises error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch popular exercises'
    });
  }
});

// @desc    Quick workout analysis (calorie calculation)
// @route   POST /api/workouts/analyze
// @access  Public
router.post('/analyze', optionalAuth, [
  body('workout_type').notEmpty().withMessage('Workout type is required'),
  body('duration_minutes').isInt({ min: 1 }).withMessage('Duration must be at least 1 minute'),
  body('intensity_level').optional().isIn(['low', 'moderate', 'high', 'extreme'])
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

    const { workout_type, duration_minutes, intensity_level = 'moderate' } = req.body;

    // Calorie calculation based on workout type and intensity
    const calorieRates = {
      running: { low: 8, moderate: 11, high: 14, extreme: 18 },
      cycling: { low: 6, moderate: 8, high: 12, extreme: 15 },
      swimming: { low: 7, moderate: 10, high: 13, extreme: 16 },
      weightlifting: { low: 4, moderate: 6, high: 8, extreme: 10 },
      yoga: { low: 2, moderate: 3, high: 4, extreme: 5 },
      walking: { low: 3, moderate: 4, high: 5, extreme: 6 },
      dancing: { low: 4, moderate: 6, high: 8, extreme: 10 },
      boxing: { low: 8, moderate: 12, high: 15, extreme: 18 },
      pilates: { low: 3, moderate: 4, high: 5, extreme: 6 },
      hiit: { low: 8, moderate: 12, high: 16, extreme: 20 },
      basketball: { low: 6, moderate: 8, high: 10, extreme: 12 },
      tennis: { low: 5, moderate: 7, high: 9, extreme: 11 },
      soccer: { low: 6, moderate: 8, high: 10, extreme: 12 },
      general: { low: 4, moderate: 6, high: 8, extreme: 10 }
    };

    const workoutKey = workout_type.toLowerCase().replace(/[^a-z]/g, '');
    const rates = calorieRates[workoutKey] || calorieRates.general;
    const caloriesPerMinute = rates[intensity_level] || rates.moderate;
    const estimatedCalories = Math.round(caloriesPerMinute * duration_minutes);

    // Performance score calculation
    const performanceScore = Math.min(100, Math.round((estimatedCalories / duration_minutes) * 5));

    const response = {
      success: true,
      data: {
        workout_type,
        duration_minutes,
        intensity_level,
        estimated_calories: estimatedCalories,
        calories_per_minute: caloriesPerMinute,
        performance_score: performanceScore,
        recommendations: []
      }
    };

    // Add recommendations based on the analysis
    if (performanceScore < 30) {
      response.data.recommendations.push('Consider increasing workout intensity for better calorie burn');
    } else if (performanceScore > 80) {
      response.data.recommendations.push('Excellent workout intensity! Keep up the great work');
    }

    if (duration_minutes < 15) {
      response.data.recommendations.push('Try extending your workout to 20-30 minutes for optimal benefits');
    } else if (duration_minutes > 90) {
      response.data.recommendations.push('Long workout session! Make sure to stay hydrated and listen to your body');
    }

    // Save analysis if user is authenticated
    if (req.user) {
      try {
        await Workout.create({
          user: req.user.id,
          name: `${workout_type} Session`,
          type: 'other',
          exercises: [{
            name: workout_type,
            category: 'other',
            duration: duration_minutes,
            calories: estimatedCalories,
            intensity: intensity_level
          }],
          notes: 'Auto-generated from quick analysis'
        });

        response.data.saved = true;
        response.message = 'Workout analysis completed and saved';
      } catch (saveError) {
        console.error('Failed to save quick workout:', saveError);
        response.data.saved = false;
      }
    } else {
      response.data.saved = false;
      response.message = 'Workout analysis completed (login to save)';
    }

    res.json(response);

  } catch (error) {
    console.error('Workout analysis error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to analyze workout'
    });
  }
});

module.exports = router;