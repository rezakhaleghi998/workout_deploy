#!/bin/bash

echo "🚂 Deploying Fitness Tracker to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Please install it first:"
    echo "npm install -g @railway/cli"
    exit 1
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "Please log in to Railway:"
    railway login
fi

# Create new project or use existing one
echo "📁 Setting up Railway project..."
if [ ! -f "railway.json" ]; then
    echo "❌ railway.json not found. Make sure you're in the correct directory."
    exit 1
fi

# Initialize Railway project
railway login
railway link

# Set up environment variables
echo "⚙️ Setting up environment variables..."

# Required environment variables
railway variables set NODE_ENV=production
railway variables set PORT=3000

# Generate secure secrets
JWT_SECRET=$(openssl rand -hex 32)
SESSION_SECRET=$(openssl rand -hex 32)
ADMIN_PASSWORD=$(openssl rand -base64 16)

railway variables set JWT_SECRET="$JWT_SECRET"
railway variables set SESSION_SECRET="$SESSION_SECRET"
railway variables set ADMIN_PASSWORD="$ADMIN_PASSWORD"

# Admin configuration
read -p "Enter admin email (default: admin@fitness-tracker.com): " ADMIN_EMAIL
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@fitness-tracker.com}
railway variables set ADMIN_EMAIL="$ADMIN_EMAIL"

# Add MongoDB (Railway Plugin)
echo "🗄️ Setting up MongoDB..."
railway add mongodb

# Wait for MongoDB to be ready
echo "⏳ Waiting for MongoDB to be ready..."
sleep 30

# Get the MongoDB connection string
MONGODB_URI=$(railway variables get MONGO_URL)
if [ -z "$MONGODB_URI" ]; then
    MONGODB_URI=$(railway variables get DATABASE_URL)
fi

if [ -z "$MONGODB_URI" ]; then
    echo "⚠️ MongoDB connection string not found. You may need to set it manually:"
    echo "railway variables set MONGODB_URI='your-mongodb-connection-string'"
else
    echo "✅ MongoDB connection string configured"
fi

# Deploy the application
echo "🚀 Deploying application..."
railway up --detach

# Run database setup
echo "🔧 Setting up database..."
railway run node scripts/setup-database.js

echo "✅ Deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "   🌐 Your app will be available at: $(railway domain)"
echo "   📧 Admin Email: $ADMIN_EMAIL"
echo "   🔑 Admin Password: $ADMIN_PASSWORD"
echo "   🔐 JWT Secret: $JWT_SECRET"
echo ""
echo "⚠️ IMPORTANT: Save these credentials in a secure location!"
echo ""
echo "🔗 Railway Dashboard: https://railway.app/dashboard"
echo "📊 Admin Panel: $(railway domain)/admin"
echo "🏥 Health Check: $(railway domain)/health"
echo ""
echo "📝 Next Steps:"
echo "   1. Visit your app URL to test the deployment"
echo "   2. Log in to the admin panel with the credentials above"
echo "   3. Update your frontend to point to the new API URL"
echo "   4. Set up custom domain (optional)"