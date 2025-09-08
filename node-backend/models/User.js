const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: [true, 'Username is required'],
    unique: true,
    trim: true,
    minlength: [3, 'Username must be at least 3 characters long'],
    maxlength: [30, 'Username cannot exceed 30 characters']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
  },
  password: {
    type: String,
    required: [true, 'Password is required'],
    minlength: [6, 'Password must be at least 6 characters long']
  },
  profile: {
    firstName: {
      type: String,
      trim: true,
      maxlength: [50, 'First name cannot exceed 50 characters']
    },
    lastName: {
      type: String,
      trim: true,
      maxlength: [50, 'Last name cannot exceed 50 characters']
    },
    age: {
      type: Number,
      min: [13, 'Age must be at least 13'],
      max: [120, 'Age cannot exceed 120']
    },
    height: {
      type: Number, // in cm
      min: [50, 'Height must be at least 50cm'],
      max: [300, 'Height cannot exceed 300cm']
    },
    weight: {
      type: Number, // in kg
      min: [20, 'Weight must be at least 20kg'],
      max: [500, 'Weight cannot exceed 500kg']
    },
    gender: {
      type: String,
      enum: ['male', 'female', 'other', 'prefer-not-to-say'],
      default: 'prefer-not-to-say'
    },
    fitnessLevel: {
      type: String,
      enum: ['beginner', 'intermediate', 'advanced', 'expert'],
      default: 'beginner'
    },
    goals: [{
      type: {
        type: String,
        enum: ['weight_loss', 'muscle_gain', 'endurance', 'strength', 'general_fitness'],
        required: true
      },
      target: Number,
      deadline: Date,
      achieved: {
        type: Boolean,
        default: false
      },
      createdAt: {
        type: Date,
        default: Date.now
      }
    }],
    preferences: {
      units: {
        weight: {
          type: String,
          enum: ['kg', 'lbs'],
          default: 'kg'
        },
        height: {
          type: String,
          enum: ['cm', 'ft'],
          default: 'cm'
        },
        distance: {
          type: String,
          enum: ['km', 'miles'],
          default: 'km'
        }
      },
      notifications: {
        workoutReminders: {
          type: Boolean,
          default: true
        },
        goalDeadlines: {
          type: Boolean,
          default: true
        },
        weeklyReports: {
          type: Boolean,
          default: true
        }
      }
    }
  },
  statistics: {
    totalWorkouts: {
      type: Number,
      default: 0
    },
    totalCaloriesBurned: {
      type: Number,
      default: 0
    },
    averageWorkoutDuration: {
      type: Number,
      default: 0
    },
    longestStreak: {
      type: Number,
      default: 0
    },
    currentStreak: {
      type: Number,
      default: 0
    },
    lastWorkoutDate: Date,
    joinDate: {
      type: Date,
      default: Date.now
    }
  },
  role: {
    type: String,
    enum: ['user', 'admin', 'moderator'],
    default: 'user'
  },
  isActive: {
    type: Boolean,
    default: true
  },
  emailVerified: {
    type: Boolean,
    default: false
  },
  emailVerificationToken: String,
  passwordResetToken: String,
  passwordResetExpires: Date,
  lastLogin: Date,
  loginAttempts: {
    type: Number,
    default: 0
  },
  lockUntil: Date
}, {
  timestamps: true
});

// Virtual for full name
userSchema.virtual('profile.fullName').get(function() {
  return `${this.profile.firstName} ${this.profile.lastName}`.trim();
});

// Virtual for BMI calculation
userSchema.virtual('profile.bmi').get(function() {
  if (this.profile.height && this.profile.weight) {
    const heightInMeters = this.profile.height / 100;
    return (this.profile.weight / (heightInMeters * heightInMeters)).toFixed(1);
  }
  return null;
});

// Index for better performance
userSchema.index({ email: 1 });
userSchema.index({ username: 1 });
userSchema.index({ 'statistics.totalWorkouts': -1 });
userSchema.index({ createdAt: -1 });

// Pre-save middleware to hash password
userSchema.pre('save', async function(next) {
  // Only hash the password if it has been modified (or is new)
  if (!this.isModified('password')) return next();

  try {
    // Hash password with cost of 12
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Method to check password
userSchema.methods.matchPassword = async function(enteredPassword) {
  return await bcrypt.compare(enteredPassword, this.password);
};

// Method to update workout statistics
userSchema.methods.updateWorkoutStats = function(caloriesBurned, duration) {
  this.statistics.totalWorkouts += 1;
  this.statistics.totalCaloriesBurned += caloriesBurned;
  
  // Update average workout duration
  const totalDuration = (this.statistics.averageWorkoutDuration * (this.statistics.totalWorkouts - 1)) + duration;
  this.statistics.averageWorkoutDuration = Math.round(totalDuration / this.statistics.totalWorkouts);
  
  // Update workout streak
  const today = new Date();
  const lastWorkout = this.statistics.lastWorkoutDate;
  
  if (lastWorkout) {
    const daysDiff = Math.floor((today - lastWorkout) / (1000 * 60 * 60 * 24));
    if (daysDiff === 1) {
      this.statistics.currentStreak += 1;
    } else if (daysDiff > 1) {
      this.statistics.currentStreak = 1;
    }
  } else {
    this.statistics.currentStreak = 1;
  }
  
  // Update longest streak
  if (this.statistics.currentStreak > this.statistics.longestStreak) {
    this.statistics.longestStreak = this.statistics.currentStreak;
  }
  
  this.statistics.lastWorkoutDate = today;
  this.lastLogin = today;
  
  return this.save();
};

// Method to get user performance metrics
userSchema.methods.getPerformanceMetrics = function() {
  const daysSinceJoining = Math.floor((Date.now() - this.statistics.joinDate) / (1000 * 60 * 60 * 24));
  const averageWorkoutsPerWeek = daysSinceJoining > 0 ? 
    Math.round((this.statistics.totalWorkouts / daysSinceJoining) * 7 * 10) / 10 : 0;
  
  return {
    totalWorkouts: this.statistics.totalWorkouts,
    totalCaloriesBurned: this.statistics.totalCaloriesBurned,
    averageWorkoutDuration: this.statistics.averageWorkoutDuration,
    currentStreak: this.statistics.currentStreak,
    longestStreak: this.statistics.longestStreak,
    averageWorkoutsPerWeek: averageWorkoutsPerWeek,
    memberSince: daysSinceJoining,
    bmi: this.profile.bmi
  };
};

// Method to check if account is locked
userSchema.methods.isLocked = function() {
  return !!(this.lockUntil && this.lockUntil > Date.now());
};

// Method to increment login attempts
userSchema.methods.incLoginAttempts = function() {
  // If we have a previous lock that has expired, restart at 1
  if (this.lockUntil && this.lockUntil < Date.now()) {
    return this.updateOne({
      $unset: {
        lockUntil: 1
      },
      $set: {
        loginAttempts: 1
      }
    });
  }
  
  const updates = { $inc: { loginAttempts: 1 } };
  
  // Lock account after 5 attempts for 2 hours
  if (this.loginAttempts + 1 >= 5 && !this.isLocked()) {
    updates.$set = { lockUntil: Date.now() + 2 * 60 * 60 * 1000 };
  }
  
  return this.updateOne(updates);
};

// Static method to find users for leaderboard
userSchema.statics.getLeaderboard = function(limit = 10) {
  return this.find({ isActive: true })
    .select('username profile.firstName profile.lastName statistics')
    .sort({ 'statistics.totalCaloriesBurned': -1 })
    .limit(limit);
};

// Transform JSON output
userSchema.methods.toJSON = function() {
  const user = this.toObject();
  delete user.password;
  delete user.emailVerificationToken;
  delete user.passwordResetToken;
  delete user.passwordResetExpires;
  delete user.loginAttempts;
  delete user.lockUntil;
  return user;
};

module.exports = mongoose.model('User', userSchema);