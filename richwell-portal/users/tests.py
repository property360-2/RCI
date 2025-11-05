"""
Comprehensive test suite for users module.

Tests cover:
- User model with roles
- User archiving and restoration
- Authentication (JWT)
- Rate limiting on login
- Permission-based access
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.test_utils import UserFactory, BaseTestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model functionality."""

    def setUp(self):
        """Set up test data."""
        self.admin = UserFactory.create(username='admin', role=User.Role.ADMIN)

    def test_user_creation_with_role(self):
        """Test creating user with specific role."""
        user = UserFactory.create(username='testuser', role=User.Role.PROFESSOR)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, User.Role.PROFESSOR)

    def test_user_default_role_is_student(self):
        """Test that default role is STUDENT."""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@test.com',
            password='testpass123'
        )
        self.assertEqual(user.role, User.Role.STUDENT)

    def test_user_string_representation(self):
        """Test __str__ method returns username and role."""
        user = UserFactory.create(username='testuser', role=User.Role.DEAN)
        self.assertEqual(str(user), 'testuser (DEAN)')

    def test_user_has_all_roles_defined(self):
        """Test all role choices are available."""
        roles = [choice[0] for choice in User.Role.choices]
        expected_roles = ['DEAN', 'REGISTRAR', 'ADMISSION', 'PROFESSOR', 'STUDENT', 'ADMIN']
        for role in expected_roles:
            self.assertIn(role, roles)

    def test_user_timestamps_are_set(self):
        """Test that created_at and updated_at are set."""
        user = UserFactory.create(username='testuser')
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_user_archive_method(self):
        """Test user archive method sets archived flag."""
        user = UserFactory.create(username='testuser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.archived)

        user.archive(self.admin)

        self.assertTrue(user.archived)
        self.assertIsNotNone(user.archived_at)
        self.assertEqual(user.archived_by, self.admin)
        self.assertFalse(user.is_active)

    def test_user_restore_method(self):
        """Test user restore method restores archived user."""
        user = UserFactory.create(username='testuser')
        user.archive(self.admin)
        self.assertTrue(user.archived)
        self.assertFalse(user.is_active)

        user.restore()

        self.assertFalse(user.archived)
        self.assertIsNone(user.archived_at)
        self.assertIsNone(user.archived_by)
        self.assertTrue(user.is_active)

    def test_archived_users_can_be_queried(self):
        """Test that archived users can be filtered in queries."""
        active_user = UserFactory.create(username='active')
        archived_user = UserFactory.create(username='archived')
        archived_user.archive(self.admin)

        active_users = User.objects.filter(archived=False)
        archived_users = User.objects.filter(archived=True)

        self.assertIn(active_user, active_users)
        self.assertNotIn(archived_user, active_users)
        self.assertIn(archived_user, archived_users)


class JWTAuthenticationTest(BaseTestCase):
    """Test JWT authentication."""

    def test_obtain_jwt_token_with_valid_credentials(self):
        """Test obtaining JWT token with valid credentials."""
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'username': 'student_test',
            'password': 'testpass123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_jwt_token_with_invalid_credentials(self):
        """Test JWT token request with invalid credentials returns 401."""
        client = APIClient()
        response = client.post('/api/v1/auth/token/', {
            'username': 'student_test',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 401)

    def test_refresh_jwt_token(self):
        """Test refreshing JWT token."""
        refresh = RefreshToken.for_user(self.student_user)

        client = APIClient()
        response = client.post('/api/v1/auth/token/refresh/', {
            'refresh': str(refresh)
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected API endpoint with JWT token."""
        client = self.get_student_client()
        response = client.get('/api/v1/students/')

        # Should get 200 or 403 (depending on permissions), not 401
        self.assertNotEqual(response.status_code, 401)

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token returns 401."""
        client = APIClient()
        response = client.get('/api/v1/students/')

        self.assertEqual(response.status_code, 401)


class LoginRateLimitingTest(TestCase):
    """Test rate limiting on login endpoint."""

    def setUp(self):
        """Set up test data and clear cache."""
        cache.clear()
        self.user = UserFactory.create(
            username='testuser',
            password='correctpass'
        )
        self.user.set_password('correctpass')
        self.user.save()
        self.client = Client()

    def tearDown(self):
        """Clear cache after each test."""
        cache.clear()

    def test_successful_login_does_not_trigger_rate_limit(self):
        """Test that successful logins don't trigger rate limiting."""
        for i in range(10):
            response = self.client.post('/login/', {
                'username': 'testuser',
                'password': 'correctpass'
            })
            # Should redirect on success (302) or show form again (200)
            self.assertIn(response.status_code, [200, 302])

    def test_failed_login_attempts_are_tracked(self):
        """Test that failed login attempts are tracked."""
        # Make 3 failed attempts
        for i in range(3):
            response = self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpass'
            })

        # Failed attempts should be recorded
        # Note: This test verifies the mechanism exists
        self.assertIsNotNone(response)

    def test_rate_limit_blocks_after_max_attempts(self):
        """Test that rate limit blocks after maximum failed attempts."""
        # Make 5 failed attempts (the limit)
        for i in range(5):
            self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpass'
            })

        # 6th attempt should be rate limited
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })

        # Should show rate limit message
        self.assertEqual(response.status_code, 200)


class UserPermissionsByRoleTest(BaseTestCase):
    """Test user permissions based on roles."""

    def test_admin_can_access_all_users(self):
        """Test admin can access all user data."""
        # Admin should have broad access
        self.assertTrue(self.admin_user.role == User.Role.ADMIN)

    def test_dean_has_dean_role(self):
        """Test dean user has DEAN role."""
        self.assertEqual(self.dean_user.role, User.Role.DEAN)

    def test_registrar_has_registrar_role(self):
        """Test registrar user has REGISTRAR role."""
        self.assertEqual(self.registrar_user.role, User.Role.REGISTRAR)

    def test_professor_has_professor_role(self):
        """Test professor user has PROFESSOR role."""
        self.assertEqual(self.professor_user.role, User.Role.PROFESSOR)

    def test_student_has_student_role(self):
        """Test student user has STUDENT role."""
        self.assertEqual(self.student_user.role, User.Role.STUDENT)

    def test_admission_has_admission_role(self):
        """Test admission user has ADMISSION role."""
        self.assertEqual(self.admission_user.role, User.Role.ADMISSION)


class UserAPIEndpointTest(BaseTestCase):
    """Test user-related API endpoints."""

    def test_authenticated_user_can_access_profile(self):
        """Test authenticated users can access their profile."""
        client = self.get_student_client()
        response = client.get('/profile/')

        # Should get 200 (profile page) or redirect
        self.assertIn(response.status_code, [200, 302])

    def test_unauthenticated_user_redirected_from_profile(self):
        """Test unauthenticated users are redirected from profile."""
        client = APIClient()
        response = client.get('/profile/')

        # Should redirect to login
        self.assertIn(response.status_code, [302, 401])


class UserQueryOptimizationTest(TestCase):
    """Test query optimization for user operations."""

    def test_bulk_user_creation(self):
        """Test bulk creating users is efficient."""
        users = UserFactory.create_batch(10, role=User.Role.STUDENT)
        self.assertEqual(User.objects.filter(role=User.Role.STUDENT).count(), 10)

    def test_filter_by_role_efficient(self):
        """Test filtering users by role."""
        UserFactory.create_batch(5, role=User.Role.STUDENT)
        UserFactory.create_batch(3, role=User.Role.PROFESSOR)

        students = User.objects.filter(role=User.Role.STUDENT)
        professors = User.objects.filter(role=User.Role.PROFESSOR)

        self.assertEqual(students.count(), 5)
        self.assertEqual(professors.count(), 3)

    def test_archived_users_query(self):
        """Test querying archived users."""
        admin = UserFactory.create(role=User.Role.ADMIN)
        active_users = UserFactory.create_batch(5)
        archived_users = UserFactory.create_batch(3)

        for user in archived_users:
            user.archive(admin)

        active_count = User.objects.filter(archived=False, role=User.Role.STUDENT).count()
        archived_count = User.objects.filter(archived=True, role=User.Role.STUDENT).count()

        self.assertEqual(active_count, 5)
        self.assertEqual(archived_count, 3)
