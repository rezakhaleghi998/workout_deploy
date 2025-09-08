const mongoose = require('mongoose');

const exerciseSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Exercise name is required'],
    trim: true
  },
  category: {
    type: String,
    enum: ['cardio', 'strength', 'flexibility', 'sports', 'other'],
    required: true
  },
  duration: {
    type: Number, // in minutes
    required: [true, 'Duration is required'],
    min: [1, 'Duration must be at least 1 minute']
  },
  calories: {
    type: Number,
    required: [true, 'Calories burned is required'],
    min: [0, 'Calories cannot be negative']
  },
  intensity: {
    type: String,
    enum: ['low', 'moderate', 'high', 'extreme'],
    default: 'moderate'
  },
  // Strength training specific
  sets: {
    type: Number,
    min: [1, 'Sets must be at least 1']
  },
  reps: {
    type: Number,
    min: [1, 'Reps must be at least 1']
  },
  weight: {
    type: Number, // in kg
    min: [0, 'Weight cannot be negative']
  },
  // Cardio specific
  distance: {
    type: Number, // in km
    min: [0, 'Distance cannot be negative']
  },
  pace: {
    type: Number, // minutes per km
    min: [0, 'Pace cannot be negative']
  },
  heartRate: {
    avg: {
      type: Number,
      min: [30, 'Heart rate too low'],
      max: [220, 'Heart rate too high']
    },
    max: {
      type: Number,
      min: [30, 'Heart rate too low'],
      max: [220, 'Heart rate too high']
    }
  },
  notes: {
    type: String,
    maxlength: [500, 'Notes cannot exceed 500 characters']
  }
});

const workoutSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  name: {
    type: String,
    required: [true, 'Workout name is required'],
    trim: true,
    maxlength: [100, 'Workout name cannot exceed 100 characters']
  },
  type: {
    type: String,
    enum: ['cardio', 'strength', 'mixed', 'flexibility', 'sports', 'other'],
    required: true
  },
  exercises: [exerciseSchema],
  totalDuration: {
    type: Number, // in minutes
    required: true,
    min: [1, 'Total duration must be at least 1 minute']
  },
  totalCalories: {
    type: Number,
    required: true,
    min: [0, 'Total calories cannot be negative']
  },
  overallIntensity: {
    type: String,
    enum: ['low', 'moderate', 'high', 'extreme'],
    default: 'moderate'
  },
  notes: {
    type: String,
    maxlength: [1000, 'Notes cannot exceed 1000 characters']
  },
  date: {
    type: Date,
    default: Date.now
  },
  mood: {
    before: {
      type: String,
      enum: ['terrible', 'bad', 'okay', 'good', 'excellent']
    },
    after: {
      type: String,
      enum: ['terrible', 'bad', 'okay', 'good', 'excellent']
    }
  },
  rating: {
    type: Number,
    min: [1, 'Rating must be between 1 and 5'],
    max: [5, 'Rating must be between 1 and 5']
  },
  tags: [{
    type: String,
    trim: true,
    maxlength: [30, 'Tag cannot exceed 30 characters']
  }],
  isTemplate: {
    type: Boolean,
    default: false
  },
  templateName: {
    type: String,
    trim: true,
    maxlength: [100, 'Template name cannot exceed 100 characters']
  },
  // Performance metrics
  metrics: {
    averageHeartRate: Number,
    maxHeartRate: Number,
    recoveryTime: Number, // in minutes
    difficulty: {
      type: Number,
      min: [1, 'Difficulty must be between 1 and 10'],
      max: [10, 'Difficulty must be between 1 and 10']
    }
  },
  // Location data (optional)
  location: {
    name: {
      type: String,
      maxlength: [100, 'Location name cannot exceed 100 characters']
    },
    type: {
      type: String,
      enum: ['gym', 'home', 'outdoor', 'studio', 'pool', 'track', 'other']
    },
    coordinates: {
      latitude: {
        type: Number,
        min: [-90, 'Invalid latitude'],
        max: [90, 'Invalid latitude']
      },
      longitude: {
        type: Number,
        min: [-180, 'Invalid longitude'],
        max: [180, 'Invalid longitude']
      }
    }
  }
}, {
  timestamps: true
});

// Index for better performance
workoutSchema.index({ user: 1, date: -1 });
workoutSchema.index({ user: 1, type: 1 });
workoutSchema.index({ user: 1, totalCalories: -1 });
workoutSchema.index({ date: -1 });
workoutSchema.index({ tags: 1 });

// Pre-save middleware to calculate totals
workoutSchema.pre('save', function(next) {
  if (this.exercises && this.exercises.length > 0) {
    // Calculate total duration and calories from exercises
    this.totalDuration = this.exercises.reduce((total, exercise) => total + exercise.duration, 0);
    this.totalCalories = this.exercises.reduce((total, exercise) => total + exercise.calories, 0);
    
    // Calculate overall intensity
    const intensityValues = { low: 1, moderate: 2, high: 3, extreme: 4 };
    const avgIntensity = this.exercises.reduce((total, exercise) => {
      return total + intensityValues[exercise.intensity];
    }, 0) / this.exercises.length;
    
    const intensityKeys = Object.keys(intensityValues);
    this.overallIntensity = intensityKeys.find(key => intensityValues[key] >= Math.round(avgIntensity)) || 'moderate';
    
    // Calculate average heart rate if available
    const heartRates = this.exercises
      .filter(ex => ex.heartRate && ex.heartRate.avg)
      .map(ex => ex.heartRate.avg);
    
    if (heartRates.length > 0) {
      this.metrics = this.metrics || {};
      this.metrics.averageHeartRate = Math.round(
        heartRates.reduce((sum, hr) => sum + hr, 0) / heartRates.length
      );
      this.metrics.maxHeartRate = Math.max(...this.exercises
        .filter(ex => ex.heartRate && ex.heartRate.max)
        .map(ex => ex.heartRate.max)
      );
    }
  }
  
  next();
});

// Post-save middleware to update user statistics
workoutSchema.post('save', async function(doc) {
  try {
    const User = mongoose.model('User');
    const user = await User.findById(doc.user);
    if (user) {
      await user.updateWorkoutStats(doc.totalCalories, doc.totalDuration);
    }
  } catch (error) {
    console.error('Error updating user stats:', error);
  }
});

// Virtual for workout efficiency (calories per minute)
workoutSchema.virtual('efficiency').get(function() {
  return this.totalDuration > 0 ? Math.round((this.totalCalories / this.totalDuration) * 10) / 10 : 0;
});

// Method to get workout summary
workoutSchema.methods.getSummary = function() {
  return {
    id: this._id,
    name: this.name,
    type: this.type,
    totalDuration: this.totalDuration,
    totalCalories: this.totalCalories,
    overallIntensity: this.overallIntensity,
    efficiency: this.efficiency,
    exerciseCount: this.exercises.length,
    date: this.date,
    rating: this.rating
  };
};

// Static method to get user's workout history
workoutSchema.statics.getUserHistory = function(userId, limit = 10, skip = 0) {
  return this.find({ user: userId })
    .sort({ date: -1 })
    .limit(limit)
    .skip(skip)
    .select('name type totalDuration totalCalories overallIntensity date rating exercises');
};

// Static method to get workout analytics
workoutSchema.statics.getAnalytics = function(userId, startDate, endDate) {
  const matchStage = { user: mongoose.Types.ObjectId(userId) };
  
  if (startDate && endDate) {
    matchStage.date = { $gte: new Date(startDate), $lte: new Date(endDate) };
  }
  
  return this.aggregate([
    { $match: matchStage },
    {
      $group: {
        _id: null,
        totalWorkouts: { $sum: 1 },
        totalCalories: { $sum: '$totalCalories' },
        totalDuration: { $sum: '$totalDuration' },
        averageCalories: { $avg: '$totalCalories' },
        averageDuration: { $avg: '$totalDuration' },
        workoutTypes: { $push: '$type' }
      }
    },
    {
      $project: {
        _id: 0,
        totalWorkouts: 1,
        totalCalories: 1,
        totalDuration: 1,
        averageCalories: { $round: ['$averageCalories', 1] },
        averageDuration: { $round: ['$averageDuration', 1] },
        workoutTypeBreakdown: {
          $reduce: {
            input: '$workoutTypes',
            initialValue: {},
            in: {
              $mergeObjects: [
                '$$value',
                {
                  $arrayToObject: [
                    [{
                      k: '$$this',
                      v: {
                        $add: [
                          { $ifNull: [{ $getField: { field: '$$this', input: '$$value' } }, 0] },
                          1
                        ]
                      }
                    }]
                  ]
                }
              ]
            }
          }
        }
      }
    }
  ]);
};

// Static method to get popular exercises
workoutSchema.statics.getPopularExercises = function(limit = 10) {
  return this.aggregate([
    { $unwind: '$exercises' },
    {
      $group: {
        _id: '$exercises.name',
        count: { $sum: 1 },
        averageCalories: { $avg: '$exercises.calories' },
        averageDuration: { $avg: '$exercises.duration' },
        category: { $first: '$exercises.category' }
      }
    },
    { $sort: { count: -1 } },
    { $limit: limit }
  ]);
};

// Transform JSON output
workoutSchema.methods.toJSON = function() {
  const workout = this.toObject({ virtuals: true });
  return workout;
};

module.exports = mongoose.model('Workout', workoutSchema);