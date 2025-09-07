# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=fitness_tracker.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Workout Calorie Predictor with Admin System..."\n\
echo "🗃️ Running migrations..."\n\
python manage.py migrate\n\
echo "👤 Creating admin user..."\n\
python manage.py shell -c "\
from fitness_app.models import User; \
User.objects.get_or_create(username=\"admin\", defaults={\"email\": \"admin@workout.com\", \"is_staff\": True, \"is_superuser\": True})[0].set_password(\"admin123\"); \
User.objects.filter(username=\"admin\").first().save(); \
print(\"✅ Admin user ready: admin/admin123\")\
"\n\
echo "🎉 Starting server..."\n\
echo "🔗 Access your app at: http://localhost:8000"\n\
echo "🎛️ Admin panel at: http://localhost:8000/admin/"\n\
python manage.py runserver 0.0.0.0:8000' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["/app/start.sh"]
