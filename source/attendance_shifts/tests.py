from datetime import time, date
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import WorkShift, EmployeeShiftAssignment

User = get_user_model()

class WorkShiftModelTest(TestCase):
    """Test suite for WorkShift model creation and string representation."""
    
    def test_work_shift_creation(self):
        shift = WorkShift.objects.create(
            name="Morning Shift",
            start_time=time(8, 0, 0),
            end_time=time(17, 0, 0),
            grace_period_minutes=10
        )
        self.assertEqual(shift.name, "Morning Shift")
        self.assertEqual(shift.grace_period_minutes, 10)
        self.assertEqual(str(shift), "Morning Shift (08:00:00 - 17:00:00)")


class WorkShiftAPITest(APITestCase):
    """Test suite for WorkShift API endpoints and permissions."""

    def setUp(self):
        # Create a test user and authenticate the test client
        self.user = User.objects.create_user(username="hr_admin", password="password123")
        self.client.force_authenticate(user=self.user)
        
        # Create sample shift data
        self.shift = WorkShift.objects.create(
            name="Night Shift",
            start_time=time(22, 0, 0),
            end_time=time(6, 0, 0)
        )

    def test_list_work_shifts(self):
        """Ensure authenticated users can list work shifts via API."""
        response = self.client.get('/api/work-shifts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Handle paginated or non-paginated responses safely
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], "Night Shift")

    def test_create_work_shift(self):
        """Ensure administrators can create a new work shift via API."""
        data = {
            "name": "Evening Shift",
            "start_time": "14:00:00",
            "end_time": "22:00:00",
            "grace_period_minutes": 15
        }
        response = self.client.post('/api/work-shifts/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkShift.objects.count(), 2)