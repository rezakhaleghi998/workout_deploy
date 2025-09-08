# Deploy to Render

This guide will help you deploy your Fitness Tracker API to Render for free.

## Prerequisites

- A GitHub account with your code repository
- A Render account (free) - [Sign up here](https://render.com)

## Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

## Step 2: Deploy to Render

### Option A: Using Render Dashboard (Recommended)

1. **Log in to Render**: Go to [render.com](https://render.com) and log in

2. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your fitness tracker repository

3. **Configure the Service**:
   - **Name**: `fitness-tracker-api`
   - **Environment**: `Node`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`

4. **Set Environment Variables**:
   Click "Advanced" and add these environment variables:
   
   ```env
   NODE_ENV=production
   PORT=10000
   JWT_SECRET=your-super-secure-jwt-secret-change-this
   SESSION_SECRET=your-super-secure-session-secret-change-this
   ADMIN_EMAIL=admin@yourdomain.com
   ADMIN_PASSWORD=YourSecurePassword123!
   ```

5. **Create MongoDB Database**:
   - Go back to Dashboard
   - Click "New +" → "PostgreSQL" (free tier)
   - Or use MongoDB Atlas (recommended)

6. **Get MongoDB Connection String**:
   - If using MongoDB Atlas: Get connection string from Atlas dashboard
   - Add it as environment variable: `MONGODB_URI=mongodb+srv://...`

7. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)

### Option B: Using render.yaml (Infrastructure as Code)

1. **Use the provided render.yaml**:
   The `render.yaml` file is already configured in your project.

2. **Deploy via Blueprint**:
   - In Render Dashboard, click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect and use `render.yaml`

## Step 3: Set Up Database

1. **Access your deployed service**:
   - Go to your service dashboard
   - Click "Shell" to open a terminal

2. **Run database setup**:
   ```bash
   node scripts/setup-database.js
   ```

3. **Verify deployment**:
   - Visit your app URL: `https://your-app-name.onrender.com`
   - Check health endpoint: `https://your-app-name.onrender.com/health`
   - Access admin panel: `https://your-app-name.onrender.com/admin`

## Step 4: Configure Custom Domain (Optional)

1. **In Render Dashboard**:
   - Go to your service settings
   - Click "Custom Domains"
   - Add your domain
   - Follow DNS configuration instructions

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `NODE_ENV` | Environment | `production` |
| `PORT` | Server port | `10000` (Render default) |
| `MONGODB_URI` | Database connection | `mongodb+srv://user:pass@cluster.mongodb.net/fitness` |
| `JWT_SECRET` | JWT signing secret | Use a long random string |
| `SESSION_SECRET` | Session secret | Use a long random string |
| `ADMIN_EMAIL` | Admin user email | `admin@yourdomain.com` |
| `ADMIN_PASSWORD` | Admin password | Strong password |

## Troubleshooting

### Common Issues:

1. **Build Fails**:
   - Check that `package.json` has correct Node version
   - Ensure all dependencies are in `dependencies` not `devDependencies`

2. **Database Connection Fails**:
   - Verify `MONGODB_URI` is correct
   - Check MongoDB Atlas network access settings
   - Ensure database user has correct permissions

3. **App Crashes on Start**:
   - Check logs in Render dashboard
   - Verify environment variables are set
   - Check that `PORT` is set to `10000`

4. **Static Files Not Loading**:
   - Ensure `public` directory is in your repository
   - Check that static routes are configured correctly

### Getting Help:

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **MongoDB Atlas Docs**: https://docs.atlas.mongodb.com

## Free Tier Limitations

- **Web Service**: 750 hours/month (enough for one always-on service)
- **Bandwidth**: 100 GB/month
- **Build Minutes**: 500 minutes/month
- **Database**: 512 MB storage (MongoDB Atlas free tier)

## Scaling Up

When you're ready to scale:

1. **Upgrade to Paid Plan**: Remove sleep mode, get more resources
2. **Add Redis**: For session storage and caching
3. **Set Up Monitoring**: Health checks, alerts, and logging
4. **Enable Auto-Deploy**: Automatic deployments from GitHub

## Security Checklist

- [ ] Change default admin password
- [ ] Use strong JWT and session secrets
- [ ] Enable HTTPS (automatic on Render)
- [ ] Set up proper CORS origins
- [ ] Monitor logs for security issues
- [ ] Regular security updates

Your Fitness Tracker API should now be deployed and accessible on Render! 🎉