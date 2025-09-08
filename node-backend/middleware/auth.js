const jwt = require('jsonwebtoken');
const User = require('../models/User');

// Generate JWT token
const generateToken = (id) => {
  return jwt.sign({ id }, process.env.JWT_SECRET || 'fallback-secret', {
    expiresIn: process.env.JWT_EXPIRE || '7d'
  });
};

// Protect routes - verify JWT token
const protect = async (req, res, next) => {
  let token;

  // Check for token in headers
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    try {
      // Get token from header
      token = req.headers.authorization.split(' ')[1];

      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret');

      // Get user from token
      req.user = await User.findById(decoded.id).select('-password');

      if (!req.user) {
        return res.status(401).json({
          success: false,
          message: 'User not found'
        });
      }

      if (!req.user.isActive) {
        return res.status(401).json({
          success: false,
          message: 'Account is deactivated'
        });
      }

      next();
    } catch (error) {
      console.error('Auth middleware error:', error);
      return res.status(401).json({
        success: false,
        message: 'Not authorized, token failed'
      });
    }
  }

  // Check for token in session (fallback for web sessions)
  else if (req.session && req.session.userId) {
    try {
      req.user = await User.findById(req.session.userId).select('-password');
      
      if (!req.user) {
        req.session.destroy();
        return res.status(401).json({
          success: false,
          message: 'User not found'
        });
      }

      if (!req.user.isActive) {
        req.session.destroy();
        return res.status(401).json({
          success: false,
          message: 'Account is deactivated'
        });
      }

      next();
    } catch (error) {
      console.error('Session auth error:', error);
      return res.status(401).json({
        success: false,
        message: 'Authentication failed'
      });
    }
  }

  else {
    return res.status(401).json({
      success: false,
      message: 'Not authorized, no token provided'
    });
  }
};

// Optional authentication - doesn't require token but populates user if present
const optionalAuth = async (req, res, next) => {
  let token;

  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    try {
      token = req.headers.authorization.split(' ')[1];
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret');
      req.user = await User.findById(decoded.id).select('-password');
    } catch (error) {
      // Token invalid but continue without user
      req.user = null;
    }
  } else if (req.session && req.session.userId) {
    try {
      req.user = await User.findById(req.session.userId).select('-password');
    } catch (error) {
      req.user = null;
    }
  }

  next();
};

// Admin authorization
const authorize = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: 'Not authorized'
      });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: `Role ${req.user.role} is not authorized to access this route`
      });
    }

    next();
  };
};

// Rate limiting for authentication endpoints
const authRateLimit = (maxAttempts = 5, windowMs = 15 * 60 * 1000) => {
  const attempts = new Map();

  return (req, res, next) => {
    const key = req.ip + req.body.email;
    const now = Date.now();
    
    if (attempts.has(key)) {
      const userAttempts = attempts.get(key);
      const recentAttempts = userAttempts.filter(time => now - time < windowMs);
      
      if (recentAttempts.length >= maxAttempts) {
        return res.status(429).json({
          success: false,
          message: 'Too many login attempts, please try again later'
        });
      }
      
      attempts.set(key, [...recentAttempts, now]);
    } else {
      attempts.set(key, [now]);
    }

    next();
  };
};

// Account lockout middleware
const checkAccountLockout = async (req, res, next) => {
  try {
    if (req.body.email) {
      const user = await User.findOne({ email: req.body.email.toLowerCase() });
      
      if (user && user.isLocked()) {
        const lockTimeRemaining = Math.ceil((user.lockUntil - Date.now()) / (1000 * 60));
        return res.status(423).json({
          success: false,
          message: `Account is locked. Try again in ${lockTimeRemaining} minutes.`
        });
      }
    }
    
    next();
  } catch (error) {
    next(error);
  }
};

module.exports = {
  generateToken,
  protect,
  optionalAuth,
  authorize,
  authRateLimit,
  checkAccountLockout
};