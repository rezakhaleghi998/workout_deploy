# Django Migration Dependency Fix Guide

## Problem Overview

Your Django app is failing deployment with an `InconsistentMigrationHistory` error:
```
Migration admin.0001_initial is applied before its dependency fitness_app.0001_initial
```

This happens because you have a custom User model (`AUTH_USER_MODEL = 'fitness_app.User'`) but Django's admin migrations were applied before your custom User model migration, creating a dependency conflict.

## Root Cause

1. **Custom User Model**: Your `fitness_app.User` model replaces Django's default User model
2. **Migration Order**: Django admin migrations expect the User model to exist first
3. **Dependency Chain**: `admin.0001_initial` depends on `auth.0012_*` which depends on your custom User model

## Quick Fix Options

### Option 1: Automated PowerShell Script (Recommended for Windows)

Run the PowerShell script I created:

```powershell
.\fix_migrations.ps1
```

This script will:
- Create a backup of your local database
- Show current migration status
- Offer gentle fix or complete reset options
- Guide you through the process step-by-step

### Option 2: Manual Commands (Step-by-step)

If you prefer manual control, run these commands in order:

#### Check Current State
```bash
python manage.py showmigrations
```

#### Gentle Fix Approach (Try This First)
```bash
# 1. Fake unapply admin migrations
python manage.py migrate admin zero --fake

# 2. Fake unapply problematic auth migrations  
python manage.py migrate auth 0011 --fake

# 3. Apply fitness_app migrations first (your custom User model)
python manage.py migrate fitness_app

# 4. Apply auth migrations
python manage.py migrate auth

# 5. Apply admin migrations
python manage.py migrate admin

# 6. Apply all remaining migrations
python manage.py migrate
```

#### Complete Reset (If Gentle Fix Fails)
```bash
# 1. Fake unapply ALL migrations
python manage.py migrate fitness_app zero --fake
python manage.py migrate admin zero --fake
python manage.py migrate auth zero --fake
python manage.py migrate contenttypes zero --fake
python manage.py migrate sessions zero --fake

# 2. Apply in correct order
python manage.py migrate contenttypes
python manage.py migrate fitness_app    # Custom User model first
python manage.py migrate auth          # Auth depends on User
python manage.py migrate admin         # Admin depends on auth
python manage.py migrate sessions      # Sessions
python manage.py migrate              # Everything else
```

### Option 3: Python Script

Run the comprehensive Python script:

```bash
python fix_migrations.py
```

## Deployment Considerations

### For Render Deployment

1. **Local Fix First**: Fix migrations locally before deploying
2. **Updated Build Script**: I've updated your `build.sh` to handle migration dependencies automatically
3. **Test Locally**: Always test with `python manage.py runserver` before deploying

### Safety Measures

1. **Backup**: The scripts automatically backup your local SQLite database
2. **Fake Migrations**: Using `--fake` doesn't lose data, just resets migration tracking
3. **Production Safety**: For production, ensure your hosting provider has recent backups

## Verification Steps

After running the fix:

1. **Check Migration Status**:
   ```bash
   python manage.py showmigrations
   ```
   All migrations should show `[X]` (applied) without conflicts

2. **Test Locally**:
   ```bash
   python manage.py runserver
   ```

3. **Create Superuser** (if needed):
   ```bash
   python manage.py createsuperuser
   ```

4. **Commit and Deploy**:
   ```bash
   git add .
   git commit -m "Fix migration dependencies for custom User model"
   git push
   ```

## Why This Happens

This is a common Django issue when:
- Using a custom User model (`AUTH_USER_MODEL`)
- The custom User model migration isn't the first migration applied
- Django's built-in app migrations (admin, auth) get applied first

## Prevention for Future Projects

1. **Create Custom User Early**: Always create custom User models before running any migrations
2. **Migration Dependencies**: Ensure your custom User model migration has proper dependencies
3. **Clean Starts**: For new projects, create the custom User model before running `python manage.py migrate`

## Troubleshooting

### If the Fix Doesn't Work

1. **Check Error Messages**: Look for specific migration names in error messages
2. **Database State**: Verify your database state with `python manage.py dbshell`
3. **Manual Investigation**: Use `python manage.py sqlmigrate app_name migration_name` to see SQL
4. **Last Resort**: Delete database and start fresh (only for development!)

### Common Issues

- **Permission Errors**: Ensure you have write access to the database file
- **Environment Issues**: Make sure you're using the correct Python environment
- **File Locks**: Close any database browser tools that might lock the database

## Files Created

- `fix_migrations.py`: Comprehensive Python script with error handling
- `fix_migrations.ps1`: Windows PowerShell script with colored output
- Updated `build.sh`: Deployment script that handles migration dependencies

## Next Steps

1. Run one of the fix options above
2. Test locally to ensure everything works
3. Deploy to Render
4. Monitor deployment logs for any remaining issues

If you continue to have issues after trying these solutions, the problem might be more complex and require examining the specific migration files and database state.
