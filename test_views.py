#!/usr/bin/env python3
"""
Test script for verifying the three implemented features:
1. Grade Encoding view for professors
2. My Grades view for students
3. Rate limiting on login
"""

import sys
import os
sys.path.insert(0, '/home/user/RCI/richwell-portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

def test_rate_limiting():
    """Test rate limiting on login"""
    print("\n=== Testing Rate Limiting ===")

    client = Client()
    cache.clear()  # Clear cache first

    # Try 5 failed login attempts
    for i in range(6):
        response = client.post('/login/', {
            'username': 'baduser',
            'password': 'wrongpass'
        })
        print(f"Attempt {i+1}: Status {response.status_code}")
        if i < 5:
            assert 'Invalid username or password' in response.content.decode() or 'attempts remaining' in response.content.decode()
        else:
            # 6th attempt should be blocked
            assert 'Too Many Attempts' in response.content.decode()
            print("✓ Rate limiting working correctly!")
            break

    cache.clear()

def test_grade_encoding_view():
    """Test grade encoding view for professors"""
    print("\n=== Testing Grade Encoding View ===")

    # Check if professor exists
    prof = User.objects.filter(role='PROFESSOR').first()
    if not prof:
        print("⚠ No professor user found in database")
        return False

    client = Client()
    # Login as professor
    client.force_login(prof)

    # Access grade encoding page
    response = client.get('/grade-encoding/')
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode()
        assert 'Grade Encoding' in content
        print("✓ Grade encoding view accessible")
        return True
    else:
        print(f"✗ Grade encoding view returned {response.status_code}")
        return False

def test_my_grades_view():
    """Test my grades view for students"""
    print("\n=== Testing My Grades View ===")

    # Check if student user exists
    student_user = User.objects.filter(role='STUDENT').first()
    if not student_user:
        print("⚠ No student user found in database")
        return False

    client = Client()
    # Login as student
    client.force_login(student_user)

    # Access my grades page
    response = client.get('/my-grades/')
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        content = response.content.decode()
        assert 'My Grades' in content or 'No Grades Available' in content
        print("✓ My grades view accessible")
        return True
    else:
        print(f"✗ My grades view returned {response.status_code}")
        return False

def test_access_control():
    """Test that views enforce role-based access control"""
    print("\n=== Testing Access Control ===")

    prof = User.objects.filter(role='PROFESSOR').first()
    student = User.objects.filter(role='STUDENT').first()

    if not prof or not student:
        print("⚠ Missing test users")
        return False

    client = Client()

    # Professor should not access student view
    client.force_login(prof)
    response = client.get('/my-grades/')
    if response.status_code == 302:  # Redirect
        print("✓ Professor correctly denied access to My Grades")
    else:
        print("⚠ Professor should be redirected from My Grades")

    # Student should not access professor view
    client.force_login(student)
    response = client.get('/grade-encoding/')
    if response.status_code == 302:  # Redirect
        print("✓ Student correctly denied access to Grade Encoding")
    else:
        print("⚠ Student should be redirected from Grade Encoding")

    return True

def main():
    print("=" * 60)
    print("Testing Three Features Implementation")
    print("=" * 60)

    # Test 1: Rate Limiting
    try:
        test_rate_limiting()
    except Exception as e:
        print(f"✗ Rate limiting test failed: {e}")

    # Test 2: Grade Encoding View
    try:
        test_grade_encoding_view()
    except Exception as e:
        print(f"✗ Grade encoding test failed: {e}")

    # Test 3: My Grades View
    try:
        test_my_grades_view()
    except Exception as e:
        print(f"✗ My grades test failed: {e}")

    # Test 4: Access Control
    try:
        test_access_control()
    except Exception as e:
        print(f"✗ Access control test failed: {e}")

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
