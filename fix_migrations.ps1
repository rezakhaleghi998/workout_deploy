# Django Migration Dependency Fix Script for Windows
# Resolves InconsistentMigrationHistory error for Render deployment

Write-Host "🚀 Django Migration Dependency Fix Tool" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Function to run Django management commands safely
function Invoke-DjangoCommand {
    param($Command)
    Write-Host "Executing: python manage.py $Command" -ForegroundColor Yellow
    try {
        python manage.py $Command
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE"
        }
        Write-Host "✅ Success" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Step 0: Backup current database
Write-Host "`n📦 Step 0: Creating database backup..." -ForegroundColor Cyan
if (Test-Path "db.sqlite3") {
    Copy-Item "db.sqlite3" "db.sqlite3.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "✅ Local database backed up" -ForegroundColor Green
}
else {
    Write-Host "⚠️  No local SQLite database found" -ForegroundColor Yellow
}

# Step 1: Check current migration status
Write-Host "`n🔍 Step 1: Checking current migration status..." -ForegroundColor Cyan
python manage.py showmigrations

Write-Host "`n📋 Choose your fix strategy:" -ForegroundColor Cyan
Write-Host "1. Gentle dependency fix (recommended first try)" -ForegroundColor White
Write-Host "2. Complete migration reset (if option 1 fails)" -ForegroundColor White
Write-Host "3. Manual step-by-step commands" -ForegroundColor White
Write-Host "4. Exit" -ForegroundColor White

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n🔧 Gentle Migration Dependency Fix" -ForegroundColor Cyan
        Write-Host "=" * 40 -ForegroundColor Cyan
        
        Write-Host "`nStep 1: Fake unapply admin migrations..." -ForegroundColor Yellow
        $success = Invoke-DjangoCommand "migrate admin zero --fake"
        if (-not $success) { break }
        
        Write-Host "`nStep 2: Fake unapply problematic auth migrations..." -ForegroundColor Yellow
        $success = Invoke-DjangoCommand "migrate auth 0011 --fake"
        if (-not $success) { break }
        
        Write-Host "`nStep 3: Apply fitness_app migrations first..." -ForegroundColor Yellow
        $success = Invoke-DjangoCommand "migrate fitness_app"
        if (-not $success) { break }
        
        Write-Host "`nStep 4: Apply auth migrations..." -ForegroundColor Yellow
        $success = Invoke-DjangoCommand "migrate auth"
        if (-not $success) { break }
        
        Write-Host "`nStep 5: Apply admin migrations..." -ForegroundColor Yellow
        $success = Invoke-DjangoCommand "migrate admin"
        if (-not $success) { break }
        
        Write-Host "`nStep 6: Apply all remaining migrations..." -ForegroundColor Yellow
        $success = Invoke-DjangoCommand "migrate"
        if (-not $success) { break }
        
        Write-Host "`n✅ Gentle fix completed successfully!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "`n⚠️  WARNING: Complete migration reset will fake-unapply ALL migrations!" -ForegroundColor Red
        $confirm = Read-Host "Type 'RESET' to confirm"
        
        if ($confirm -eq "RESET") {
            Write-Host "`n🔄 Complete Migration Reset" -ForegroundColor Cyan
            Write-Host "=" * 30 -ForegroundColor Cyan
            
            Write-Host "`nStep 1: Fake unapply all migrations..." -ForegroundColor Yellow
            Invoke-DjangoCommand "migrate fitness_app zero --fake"
            Invoke-DjangoCommand "migrate admin zero --fake"
            Invoke-DjangoCommand "migrate auth zero --fake"
            Invoke-DjangoCommand "migrate contenttypes zero --fake"
            Invoke-DjangoCommand "migrate sessions zero --fake"
            
            Write-Host "`nStep 2: Apply migrations in correct order..." -ForegroundColor Yellow
            $success = Invoke-DjangoCommand "migrate contenttypes"
            if ($success) { $success = Invoke-DjangoCommand "migrate fitness_app" }
            if ($success) { $success = Invoke-DjangoCommand "migrate auth" }
            if ($success) { $success = Invoke-DjangoCommand "migrate admin" }
            if ($success) { $success = Invoke-DjangoCommand "migrate sessions" }
            if ($success) { $success = Invoke-DjangoCommand "migrate" }
            
            if ($success) {
                Write-Host "`n✅ Complete reset successful!" -ForegroundColor Green
            }
        }
        else {
            Write-Host "❌ Reset cancelled" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host "`n📋 Manual Step-by-Step Commands" -ForegroundColor Cyan
        Write-Host "Copy and run these commands one by one:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "# Check current state:" -ForegroundColor Gray
        Write-Host "python manage.py showmigrations" -ForegroundColor White
        Write-Host ""
        Write-Host "# Gentle fix approach:" -ForegroundColor Gray
        Write-Host "python manage.py migrate admin zero --fake" -ForegroundColor White
        Write-Host "python manage.py migrate auth 0011 --fake" -ForegroundColor White
        Write-Host "python manage.py migrate fitness_app" -ForegroundColor White
        Write-Host "python manage.py migrate auth" -ForegroundColor White
        Write-Host "python manage.py migrate admin" -ForegroundColor White
        Write-Host "python manage.py migrate" -ForegroundColor White
        Write-Host ""
        Write-Host "# If gentle fix fails, complete reset:" -ForegroundColor Gray
        Write-Host "python manage.py migrate fitness_app zero --fake" -ForegroundColor White
        Write-Host "python manage.py migrate admin zero --fake" -ForegroundColor White
        Write-Host "python manage.py migrate auth zero --fake" -ForegroundColor White
        Write-Host "python manage.py migrate contenttypes zero --fake" -ForegroundColor White
        Write-Host "python manage.py migrate sessions zero --fake" -ForegroundColor White
        Write-Host "python manage.py migrate contenttypes" -ForegroundColor White
        Write-Host "python manage.py migrate fitness_app" -ForegroundColor White
        Write-Host "python manage.py migrate auth" -ForegroundColor White
        Write-Host "python manage.py migrate admin" -ForegroundColor White
        Write-Host "python manage.py migrate sessions" -ForegroundColor White
        Write-Host "python manage.py migrate" -ForegroundColor White
    }
    
    "4" {
        Write-Host "👋 Exiting..." -ForegroundColor Yellow
        exit
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit
    }
}

# Final verification
Write-Host "`n🔍 Final verification - checking migration status..." -ForegroundColor Cyan
python manage.py showmigrations

Write-Host "`n📋 Next Steps for Render Deployment:" -ForegroundColor Cyan
Write-Host "1. Test locally: python manage.py runserver" -ForegroundColor White
Write-Host "2. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "3. Commit changes: git add . && git commit -m 'Fix migration dependencies'" -ForegroundColor White
Write-Host "4. Push to deploy: git push" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Important Notes:" -ForegroundColor Yellow
Write-Host "- If you have important data, restore from backup if something goes wrong" -ForegroundColor White
Write-Host "- For production deployment, Render will run migrations automatically" -ForegroundColor White
Write-Host "- Monitor Render deployment logs for any remaining issues" -ForegroundColor White
