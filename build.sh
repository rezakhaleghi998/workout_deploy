#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Fix migration dependencies for custom User model
echo "Checking and fixing migration dependencies..."

# Check if this is a fresh deployment or has migration conflicts
python manage.py showmigrations --plan > migration_plan.txt 2>&1 || true

# If migration conflicts exist, fix them
if grep -q "InconsistentMigrationHistory\|dependency" migration_plan.txt 2>/dev/null; then
    echo "Migration dependency issues detected. Fixing..."
    
    # Gentle fix approach for deployment
    echo "Applying fitness_app migrations first (custom User model)..."
    python manage.py migrate fitness_app --noinput || true
    
    echo "Applying auth migrations..."
    python manage.py migrate auth --noinput || true
    
    echo "Applying admin migrations..."
    python manage.py migrate admin --noinput || true
    
    echo "Applying all remaining migrations..."
    python manage.py migrate --noinput
else
    # Standard migration apply
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

# Clean up temporary file
rm -f migration_plan.txt

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

echo "Build completed successfully!"