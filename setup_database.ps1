# PowerShell script to configure PostgreSQL database and run migrations
# Run this script: .\setup_database.ps1

Write-Host "🚀 Setting up PostgreSQL Database for Fitness Tracker" -ForegroundColor Green

# Set environment variables
$env:DATABASE_URL = "postgresql://fitness_tracker_db_3qe6_user:oVLVrbtziMFKg6myIBOHpbOIgY5N07ph@dpg-d2u5d7mr433s73e03k00-a/fitness_tracker_db_3qe6"
$env:SECRET_KEY = "django-insecure-fitness-tracker-prod-key-2024"
$env:DEBUG = "False"

Write-Host "✅ Environment variables set" -ForegroundColor Green
Write-Host "📍 Database URL: $($env:DATABASE_URL.Substring(0,50))..." -ForegroundColor Yellow

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Blue
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Run database migrations
Write-Host "🔄 Running database migrations..." -ForegroundColor Blue
python manage.py makemigrations
python manage.py migrate

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database migrations completed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Database migrations failed" -ForegroundColor Red
    Write-Host "🔧 This might be because the database is not yet available" -ForegroundColor Yellow
    Write-Host "🔧 Try again in a few minutes or check your database status" -ForegroundColor Yellow
}

# Create superuser (optional)
Write-Host "👤 Do you want to create a superuser? (y/n)" -ForegroundColor Cyan
$createUser = Read-Host

if ($createUser -eq "y" -or $createUser -eq "Y") {
    Write-Host "Creating superuser..." -ForegroundColor Blue
    python manage.py createsuperuser
}

Write-Host "🎯 Setup complete! Your app is configured to use PostgreSQL" -ForegroundColor Green
Write-Host "🚀 Start the server with: python manage.py runserver" -ForegroundColor Cyan
