# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import UserProfile, WorkoutSession, ExerciseType

User = get_user_model()

class UserRegistrationTest(APITestCase):
    """Test user registration functionality"""
    
    def test_user_registration(self):
        """Test user can register successfully"""
        url = reverse('fitness_app:register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

class WorkoutSessionTest(APITestCase):
    """Test workout session functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.exercise_type = ExerciseType.objects.create(
            name='Running',
            calories_per_hour=500
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_workout_session(self):
        """Test creating a workout session"""
        url = reverse('fitness_app:workout_sessions')
        data = {
            'exercise_type': self.exercise_type.id,
            'duration_minutes': 30,
            'calories_burned': 250,
            'intensity': 'Medium'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(WorkoutSession.objects.filter(user=self.user).exists())
