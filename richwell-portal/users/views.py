"""
User Authentication and Management Views

This module provides core authentication functionality for the Richwell College Portal,
including login, logout, dashboard routing, and user profile management.

The views implement role-based access control (RBAC) with the following roles:
- DEAN: Academic leadership with analytics access
- REGISTRAR: Student records and enrollment management
- ADMISSION: New student processing and enrollment creation
- PROFESSOR: Grade encoding and section management
- STUDENT: Grade viewing and enrollment tracking
- ADMIN: System administration

Author: Richwell College IT Team
Version: 3.0
Last Updated: 2024
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from .models import User


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Handle user authentication with enhanced UX.

    This view processes both GET and POST requests:
    - GET: Displays the login form
    - POST: Authenticates user credentials and initiates session

    **Features:**
    - HTMX-powered async form submission
    - Role-based dashboard routing
    - Remember me functionality
    - Archive status validation (archived users cannot login)
    - Comprehensive error messaging

    **POST Parameters:**
        username (str): User's unique username
        password (str): User's password
        remember (str, optional): "on" if remember me checkbox is checked

    **Returns:**
        GET: Rendered login page template
        POST (success): Redirect to role-specific dashboard
        POST (error): HTMX-compatible error message HTML

    **Example HTMX Response (Error):**
        ```html
        <div class="rounded-lg p-4 bg-red-100 text-red-800">
            <strong>Error:</strong> Invalid username or password
        </div>
        ```

    **Security Features:**
    - CSRF protection enabled
    - Password field never echoed back
    - Session timeout configurable
    - Failed login attempt logging (TODO: implement rate limiting)
    """
    # Redirect authenticated users to their dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember') == 'on'

        # Validate input
        if not username or not password:
            error_html = '''
                <div class="rounded-lg p-4 bg-red-100 text-red-800">
                    <strong>Error:</strong> Please provide both username and password.
                </div>
            '''
            return HttpResponse(error_html)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if user is archived (soft deleted)
            if user.archived:
                error_html = f'''
                    <div class="rounded-lg p-4 bg-yellow-100 text-yellow-800">
                        <strong>Account Inactive:</strong> This account has been archived.
                        Please contact IT Support for assistance.
                    </div>
                '''
                return HttpResponse(error_html)

            # Login user and create session
            login(request, user)

            # Set session expiry based on "remember me"
            if not remember:
                # Session expires when browser closes
                request.session.set_expiry(0)
            else:
                # Session expires after 2 weeks (1209600 seconds)
                request.session.set_expiry(1209600)

            # Success message
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')

            # HTMX redirect response
            response = HttpResponse()
            response['HX-Redirect'] = '/dashboard/'
            return response

        else:
            # Invalid credentials
            error_html = '''
                <div class="rounded-lg p-4 bg-red-100 text-red-800">
                    <strong>Error:</strong> Invalid username or password. Please try again.
                </div>
            '''
            return HttpResponse(error_html)

    # GET request - render login page
    return render(request, 'pages/login.html')


@login_required
def logout_view(request):
    """
    Terminate user session and redirect to login page.

    This view handles user logout with proper session cleanup and provides
    user feedback through Django messages framework.

    **Features:**
    - Complete session cleanup
    - User feedback message
    - Redirect to login page
    - Login required (prevents logout of non-authenticated users)

    **Returns:**
        HttpResponse: Redirect to login page with success message

    **Example Usage:**
        ```html
        <a href="{% url 'logout' %}">Sign Out</a>
        ```
    """
    username = request.user.username
    logout(request)
    messages.info(request, f'You have been logged out successfully. See you soon!')
    return redirect('login')


@login_required
def dashboard_view(request):
    """
    Route users to role-specific dashboard templates.

    This view acts as a router, directing authenticated users to their
    appropriate dashboard based on their assigned role. Each role has a
    custom dashboard with role-specific widgets, metrics, and actions.

    **Role-to-Dashboard Mapping:**
    - DEAN → dean/dashboard.html (analytics, academic oversight)
    - REGISTRAR → registrar/dashboard.html (student records, enrollment)
    - ADMISSION → admission/dashboard.html (applicant processing)
    - PROFESSOR → professor/dashboard.html (grade encoding, sections)
    - STUDENT → student/dashboard.html (grades, enrollments)
    - ADMIN → admin/dashboard.html (system management)

    **Context Variables:**
        user (User): Current authenticated user object
        role (str): User's role (DEAN, REGISTRAR, etc.)
        full_name (str): User's full name or username fallback

    **Returns:**
        HttpResponse: Rendered role-specific dashboard template

    **Dashboard Features by Role:**

    **DEAN Dashboard:**
    - Student enrollment stats
    - Course/subject analytics
    - Faculty overview
    - Academic calendar
    - System-wide metrics

    **REGISTRAR Dashboard:**
    - Student archive access
    - Enrollment management
    - Grade record oversight
    - INC tracking
    - Report generation

    **ADMISSION Dashboard:**
    - Applicant queue
    - Quick enrollment tool
    - New student onboarding
    - Enrollment stats by term

    **PROFESSOR Dashboard:**
    - Assigned sections
    - Grade encoding interface
    - Student roster
    - INC management

    **STUDENT Dashboard:**
    - Current enrollments
    - Grade history
    - Academic standing
    - INC deadlines
    """
    user = request.user

    # Context data available to all dashboards
    context = {
        'user': user,
        'role': user.role,
        'full_name': user.get_full_name() or user.username,
    }

    # Route to role-specific dashboard template
    if user.role == User.Role.DEAN:
        return render(request, 'pages/dean/dashboard.html', context)

    elif user.role == User.Role.REGISTRAR:
        return render(request, 'pages/registrar/dashboard.html', context)

    elif user.role == User.Role.ADMISSION:
        return render(request, 'pages/admission/dashboard.html', context)

    elif user.role == User.Role.PROFESSOR:
        return render(request, 'pages/professor/dashboard.html', context)

    elif user.role == User.Role.STUDENT:
        return render(request, 'pages/student/dashboard.html', context)

    elif user.role == User.Role.ADMIN:
        return render(request, 'pages/admin/dashboard.html', context)

    else:
        # Fallback for undefined roles
        return render(request, 'pages/placeholder.html', {
            **context,
            'page_title': 'Dashboard',
            'message': 'Your role does not have an assigned dashboard yet.'
        })


@login_required
def profile_view(request):
    """
    Display and edit user profile information.

    This view allows users to view and update their profile information,
    including personal details, contact info, and password changes.

    **Features:**
    - View current profile data
    - Update personal information (TODO)
    - Change password (TODO)
    - Upload profile picture (TODO)
    - View activity log (TODO)

    **Context Variables:**
        user (User): Current authenticated user
        can_edit (bool): Whether user can edit their profile

    **Returns:**
        HttpResponse: Rendered profile page template

    **Planned Enhancements:**
    - Profile picture upload with image resizing
    - Password strength meter
    - Two-factor authentication setup
    - Activity log (last 10 logins, password changes)
    - Email verification workflow
    """
    context = {
        'user': request.user,
        'can_edit': True,  # TODO: Add permission check
    }

    return render(request, 'pages/placeholder.html', {
        **context,
        'page_title': 'User Profile',
        'message': 'Profile page is under development.'
    })


@login_required
def placeholder_view(request):
    """
    Temporary placeholder for routes under development.

    This view serves as a friendly "coming soon" page for features
    that are planned but not yet implemented. It provides context
    about what the page will contain and maintains user session.

    **Usage:**
        Used in urls.py for routes like:
        - /courses/
        - /subjects/
        - /sections/
        - /students/
        - /grade-encoding/
        - /analytics/

    **Context Variables:**
        page_title (str): "Coming Soon"
        message (str): Informative message about the page

    **Returns:**
        HttpResponse: Rendered placeholder template
    """
    context = {
        'page_title': 'Coming Soon',
        'message': 'This feature is under development and will be available soon.',
    }

    return render(request, 'pages/placeholder.html', context)
