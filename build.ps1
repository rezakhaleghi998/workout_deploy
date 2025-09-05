# Build script for Windows development

Write-Host "Starting build process..." -ForegroundColor Green

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Collect static files
Write-Host "Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput --clear

# Apply database migrations
Write-Host "Applying database migrations..." -ForegroundColor Yellow
python manage.py migrate --noinput

Write-Host "Build completed successfully!" -ForegroundColor Green
