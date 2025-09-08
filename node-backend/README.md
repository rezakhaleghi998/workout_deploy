# 🏋️ Fitness Tracker - Node.js API

A comprehensive fitness tracking backend API built with Node.js, Express, and MongoDB. Features user authentication, workout tracking, performance analytics, and a powerful admin dashboard.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, authentication, profiles, and preferences
- **Workout Tracking**: Create, update, delete, and analyze workouts
- **Exercise Library**: Comprehensive exercise database with categories and metrics
- **Performance Analytics**: Track progress, streaks, and performance metrics
- **Goal Setting**: Set and track fitness goals with deadlines
- **Social Features**: User leaderboards and achievement system

### Admin Dashboard
- **User Management**: View, edit, and manage all users
- **Workout Monitoring**: Track all workouts and exercise trends
- **Analytics Dashboard**: Platform-wide statistics and insights
- **System Monitoring**: Health checks and system information
- **Real-time Charts**: Interactive data visualization

### Technical Features
- **RESTful API**: Complete REST API with comprehensive endpoints
- **JWT Authentication**: Secure token-based authentication
- **Session Management**: Hybrid JWT + session authentication
- **Rate Limiting**: Built-in API rate limiting and security
- **Data Validation**: Comprehensive input validation and sanitization
- **Error Handling**: Robust error handling and logging
- **Health Monitoring**: Built-in health checks and monitoring

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Frontend Integration](#frontend-integration)
- [Admin Dashboard](#admin-dashboard)
- [Environment Configuration](#environment-configuration)
- [Database Schema](#database-schema)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## 🏃‍♂️ Quick Start

### Prerequisites
- Node.js 16+ and npm
- MongoDB database (local or MongoDB Atlas)
- Git

### 1. Clone and Install
```bash
git clone <repository-url>
cd node-backend
npm install
```

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup
```bash
# Setup database with admin user and sample data
npm run setup

# Or just create indexes and admin user
node scripts/setup-database.js
```

### 4. Start Development Server
```bash
npm run dev
```

Visit:
- **API**: http://localhost:3000
- **Health Check**: http://localhost:3000/health
- **Admin Dashboard**: http://localhost:3000/admin

## 🛠️ Installation

### Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd node-backend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Environment Configuration**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your settings:
   ```env
   NODE_ENV=development
   PORT=3000
   MONGODB_URI=mongodb://localhost:27017/fitness-tracker
   JWT_SECRET=your-jwt-secret
   SESSION_SECRET=your-session-secret
   ADMIN_EMAIL=admin@fitness-tracker.com
   ADMIN_PASSWORD=YourSecurePassword123!
   ```

4. **Database Setup**:
   ```bash
   # Option 1: Full setup with sample data
   npm run setup
   
   # Option 2: Just setup indexes and admin
   node scripts/setup-database.js
   
   # Option 3: Seed with sample data (clears existing data)
   npm run seed
   ```

5. **Start Development Server**:
   ```bash
   npm run dev
   ```

### Production Setup

1. **Environment Variables**:
   ```bash
   cp .env.example .env.production
   # Edit .env.production with production values
   ```

2. **Build and Start**:
   ```bash
   npm install --production
   npm start
   ```

## 📚 API Documentation

### Base URL
```
Development: http://localhost:3000
Production: https://your-domain.com
```

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "profile": {
    "firstName": "John",
    "lastName": "Doe",
    "age": 28,
    "height": 175,
    "weight": 70,
    "fitnessLevel": "intermediate"
  }
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

#### Get Profile
```http
GET /api/auth/profile
Authorization: Bearer <token>
```

### Workouts

#### Create Workout
```http
POST /api/workouts
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Morning Run",
  "type": "cardio",
  "exercises": [
    {
      "name": "Running",
      "category": "cardio",
      "duration": 30,
      "calories": 350,
      "intensity": "moderate",
      "distance": 5,
      "pace": 6
    }
  ],
  "notes": "Great morning run in the park"
}
```

#### Get Workouts
```http
GET /api/workouts?limit=10&page=1&type=cardio&startDate=2024-01-01
Authorization: Bearer <token>
```

#### Analyze Workout (Public)
```http
POST /api/workouts/analyze
Content-Type: application/json

{
  "workout_type": "running",
  "duration_minutes": 30,
  "intensity_level": "moderate"
}
```

### Analytics

#### Get Workout Analytics
```http
GET /api/analytics/workouts?period=month&startDate=2024-01-01&endDate=2024-01-31
Authorization: Bearer <token>
```

#### Get Performance Metrics
```http
GET /api/analytics/performance
Authorization: Bearer <token>
```

#### Get Platform Statistics (Public)
```http
GET /api/analytics/platform
```

### Users

#### Get User Statistics
```http
GET /api/users/stats
Authorization: Bearer <token>
```

#### Get Leaderboard (Public)
```http
GET /api/users/leaderboard?type=calories&limit=10
```

#### Get User Achievements
```http
GET /api/users/achievements
Authorization: Bearer <token>
```

### Admin Endpoints

All admin endpoints require `admin` or `moderator` role.

#### Get Dashboard Data
```http
GET /api/admin/dashboard
Authorization: Bearer <admin-token>
```

#### Get All Users
```http
GET /api/admin/users?page=1&limit=20&search=john&status=active&role=user
Authorization: Bearer <admin-token>
```

#### Update User
```http
PUT /api/admin/users/:id
Authorization: Bearer <admin-token>
Content-Type: application/json

{
  "role": "moderator",
  "isActive": true
}
```

## 🚀 Deployment

The application supports deployment to multiple platforms:

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy using the script
chmod +x deploy/railway-deploy.sh
./deploy/railway-deploy.sh
```

### Render
Follow the guide in `deploy/render-deploy.md` or use the `render.yaml` blueprint.

### Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Docker
```bash
# Build image
docker build -t fitness-tracker-api .

# Run with Docker Compose
docker-compose up -d
```

### Heroku
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-fitness-api

# Set environment variables
heroku config:set NODE_ENV=production
heroku config:set MONGODB_URI=your-mongodb-uri
heroku config:set JWT_SECRET=your-jwt-secret

# Deploy
git push heroku main

# Setup database
heroku run node scripts/setup-database.js
```

## 🖥️ Frontend Integration

### Using the API Client

Include the API client in your HTML:
```html
<script src="/js/api-client.js"></script>
<script src="/js/frontend-integration.js"></script>
```

### Basic Usage
```javascript
// The API client is available as window.fitnessAPI

// Register user
try {
  const response = await fitnessAPI.register({
    username: 'johndoe',
    email: 'john@example.com',
    password: 'SecurePass123!'
  });
  console.log('Registration successful:', response);
} catch (error) {
  console.error('Registration failed:', error.message);
}

// Analyze workout
const analysis = await fitnessAPI.analyzeWorkout({
  workout_type: 'running',
  duration_minutes: 30,
  intensity_level: 'moderate'
});

// Create workout (requires authentication)
const workout = await fitnessAPI.createWorkout({
  name: 'Morning Run',
  type: 'cardio',
  exercises: [...]
});
```

### Integration with Existing Django Frontend

The integration scripts automatically enhance your existing Django frontend:

1. **Authentication UI**: Adds login/register forms
2. **User Dashboard**: Shows user stats and progress
3. **Enhanced Workout Analyzer**: Integrates with the API
4. **Save Workouts**: Allows authenticated users to save workouts

## 👑 Admin Dashboard

Access the admin dashboard at `/admin` with admin credentials.

### Features:
- **Dashboard Overview**: Key metrics and charts
- **User Management**: View, edit, and manage users
- **Workout Monitoring**: Track all workouts and trends
- **Advanced Analytics**: Platform-wide insights
- **System Information**: Health and performance monitoring

### Default Admin Credentials:
- **Email**: Value from `ADMIN_EMAIL` environment variable
- **Password**: Value from `ADMIN_PASSWORD` environment variable

**⚠️ Important**: Change the default admin password after first login!

## ⚙️ Environment Configuration

### Required Variables
```env
NODE_ENV=production
PORT=3000
MONGODB_URI=mongodb://localhost:27017/fitness-tracker
JWT_SECRET=your-jwt-secret-here
SESSION_SECRET=your-session-secret-here
ADMIN_EMAIL=admin@fitness-tracker.com
ADMIN_PASSWORD=SecurePassword123!
```

### Optional Variables
```env
# CORS Configuration
FRONTEND_URL=https://your-frontend.com
ADMIN_URL=https://your-admin.com

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Rate Limiting
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_PATH=./uploads

# Logging
LOG_LEVEL=info
```

## 🗄️ Database Schema

### User Model
- **Authentication**: username, email, password (hashed)
- **Profile**: personal info, fitness level, goals, preferences
- **Statistics**: total workouts, calories burned, streaks
- **Settings**: notifications, units, privacy

### Workout Model
- **Basic Info**: name, type, date, duration, calories
- **Exercises**: array of exercise objects with details
- **Metadata**: mood, rating, notes, tags, location
- **Performance**: intensity, efficiency metrics

### Indexes
- Users: email, username, statistics, creation date
- Workouts: user + date, type, calories, exercises
- Compound indexes for common query patterns

## 🔒 Security

### Authentication & Authorization
- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt rounds
- **Session Management**: Hybrid JWT + session approach
- **Role-Based Access**: User, moderator, admin roles

### API Security
- **Rate Limiting**: Configurable per endpoint
- **CORS Protection**: Configurable origins
- **Input Validation**: Comprehensive validation with express-validator
- **SQL Injection Protection**: MongoDB + Mongoose ODM
- **XSS Protection**: Helmet.js security headers

### Data Protection
- **Environment Variables**: Sensitive data in env vars
- **Account Lockout**: Automatic lockout after failed attempts
- **Password Requirements**: Strong password validation
- **Data Sanitization**: Input cleaning and validation

## 🧪 Testing

### Run Tests
```bash
npm test
```

### Test Coverage
```bash
npm run test:coverage
```

### API Testing
Use the included Postman collection or test with curl:
```bash
# Health check
curl http://localhost:3000/health

# Register user
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"Test123!"}'
```

## 📈 Monitoring

### Health Checks
- **Endpoint**: `/health`
- **Docker**: Built-in health check
- **Kubernetes**: Readiness and liveness probes

### Logging
- **Development**: Console logging with colors
- **Production**: Structured logging (configurable)
- **Error Tracking**: Comprehensive error handling

### Metrics
- **Performance**: Response times, throughput
- **Usage**: API endpoint usage, user activity
- **Errors**: Error rates and types

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Verify connection string
echo $MONGODB_URI
```

**Authentication Issues**
```bash
# Check JWT secret is set
echo $JWT_SECRET

# Verify admin user exists
node -e "
  require('./scripts/setup-database.js');
  // Check admin user creation
"
```

**Port Already in Use**
```bash
# Find process using port 3000
lsof -ti:3000

# Kill process
kill -9 $(lsof -ti:3000)
```

**Missing Dependencies**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Debug Mode
```bash
# Enable debug logging
DEBUG=fitness-tracker:* npm run dev

# Or set LOG_LEVEL
LOG_LEVEL=debug npm run dev
```

### Database Issues
```bash
# Reset database
node scripts/setup-database.js

# Seed with sample data
npm run seed

# Check database connection
node scripts/test-db-connection.js
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow existing code style
- Add tests for new features
- Update documentation
- Use conventional commits

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: This README and inline code comments
- **Issues**: GitHub Issues for bug reports and feature requests
- **Email**: Support email from environment configuration

## 🗺️ Roadmap

- [ ] **Mobile App API**: Enhanced endpoints for mobile apps
- [ ] **Real-time Features**: WebSocket support for live updates
- [ ] **Advanced Analytics**: Machine learning insights
- [ ] **Social Features**: Following, challenges, and groups
- [ ] **Integration APIs**: Third-party fitness device integration
- [ ] **Nutrition Tracking**: Food logging and nutrition analysis
- [ ] **Workout Plans**: Structured workout programs
- [ ] **Video Integration**: Exercise video library

---

**Built with ❤️ using Node.js, Express, MongoDB, and modern web technologies**

## 🎯 Getting Started Checklist

- [ ] Install Node.js 16+ and MongoDB
- [ ] Clone repository and install dependencies
- [ ] Copy and configure `.env` file
- [ ] Run database setup script
- [ ] Start development server
- [ ] Test API health endpoint
- [ ] Access admin dashboard
- [ ] Test user registration and login
- [ ] Create a test workout
- [ ] Deploy to your preferred platform

**🚀 You're ready to build amazing fitness applications!**