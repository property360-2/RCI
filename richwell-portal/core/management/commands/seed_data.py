"""
Data Seeder Management Command

This Django management command seeds the database with comprehensive test data
for the Richwell College Portal.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first

Author: Richwell College IT Team
Version: 3.0
"""

from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.utils import timezone
from datetime import timedelta
import random

from users.models import User
from students.models import Student
from courses.models import Course
from subjects.models import Subject
from terms.models import Term
from sections.models import Section
from enrollments.models import Enrollment
from grades.models import GradeRecord


class Command(BaseCommand):
    help = 'Seed the database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        try:
            self.ensure_schema()
            with transaction.atomic():
                # Seed in order of dependencies
                users = self.seed_users()
                courses = self.seed_courses()
                subjects = self.seed_subjects(courses)
                terms = self.seed_terms()
                students = self.seed_students(users, courses)
                sections = self.seed_sections(subjects, terms, users)
                enrollments = self.seed_enrollments(students, sections, terms)
                self.seed_grades(enrollments)

                self.stdout.write(self.style.SUCCESS('Data seeding completed successfully!'))
                self.print_summary()
                self.print_credentials()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during seeding: {str(e)}'))
            raise

    def ensure_schema(self):
        """Ensure legacy databases have the expected columns before seeding."""
        self.ensure_course_schema()

    def ensure_course_schema(self):
        """Add missing columns for the Course model when older schemas are detected."""
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(courses_course)")
            columns = {row[1] for row in cursor.fetchall()}

        if not columns:
            return

        alterations = []

        with connection.cursor() as cursor:
            if 'name' not in columns:
                cursor.execute("ALTER TABLE courses_course ADD COLUMN name varchar(200)")
                cursor.execute(
                    "UPDATE courses_course "
                    "SET name = title "
                    "WHERE name IS NULL AND title IS NOT NULL"
                )
                alterations.append('name')

            if 'total_units' not in columns:
                cursor.execute("ALTER TABLE courses_course ADD COLUMN total_units integer DEFAULT 0")
                cursor.execute(
                    "UPDATE courses_course "
                    "SET total_units = 0 "
                    "WHERE total_units IS NULL"
                )
                alterations.append('total_units')

            if 'years_to_complete' not in columns:
                cursor.execute("ALTER TABLE courses_course ADD COLUMN years_to_complete integer DEFAULT 4")
                cursor.execute(
                    "UPDATE courses_course "
                    "SET years_to_complete = COALESCE(years, 4) "
                    "WHERE years_to_complete IS NULL"
                )
                alterations.append('years_to_complete')

        if alterations:
            joined = ', '.join(alterations)
            self.stdout.write(self.style.WARNING(f'Adjusted courses schema (added: {joined})'))

    def clear_data(self):
        """Clear all existing data (except superusers)."""
        GradeRecord.objects.all().delete()
        Enrollment.objects.all().delete()
        Section.objects.all().delete()
        Student.objects.all().delete()
        Subject.objects.all().delete()
        Course.objects.all().delete()
        Term.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleared'))

    def seed_users(self):
        """Create users with different roles."""
        self.stdout.write('Seeding users...')

        users_data = [
            # Admin
            {'username': 'admin', 'email': 'admin@richwell.edu', 'first_name': 'System', 'last_name': 'Administrator', 'role': 'ADMIN'},

            # Deans
            {'username': 'dean.cs', 'email': 'dean.cs@richwell.edu', 'first_name': 'Robert', 'last_name': 'Mitchell', 'role': 'DEAN'},
            {'username': 'dean.ba', 'email': 'dean.ba@richwell.edu', 'first_name': 'Sarah', 'last_name': 'Williams', 'role': 'DEAN'},

            # Registrars
            {'username': 'registrar1', 'email': 'registrar@richwell.edu', 'first_name': 'Maria', 'last_name': 'Rodriguez', 'role': 'REGISTRAR'},
            {'username': 'registrar2', 'email': 'registrar2@richwell.edu', 'first_name': 'James', 'last_name': 'Chen', 'role': 'REGISTRAR'},

            # Admission Officers
            {'username': 'admission1', 'email': 'admission@richwell.edu', 'first_name': 'Emily', 'last_name': 'Johnson', 'role': 'ADMISSION'},
            {'username': 'admission2', 'email': 'admission2@richwell.edu', 'first_name': 'David', 'last_name': 'Lee', 'role': 'ADMISSION'},

            # Professors
            {'username': 'prof.johnson', 'email': 'johnson@richwell.edu', 'first_name': 'Michael', 'last_name': 'Johnson', 'role': 'PROFESSOR'},
            {'username': 'prof.martinez', 'email': 'martinez@richwell.edu', 'first_name': 'Carlos', 'last_name': 'Martinez', 'role': 'PROFESSOR'},
            {'username': 'prof.lee', 'email': 'lee@richwell.edu', 'first_name': 'Jennifer', 'last_name': 'Lee', 'role': 'PROFESSOR'},
            {'username': 'prof.chen', 'email': 'chen@richwell.edu', 'first_name': 'Wei', 'last_name': 'Chen', 'role': 'PROFESSOR'},
            {'username': 'prof.garcia', 'email': 'garcia@richwell.edu', 'first_name': 'Ana', 'last_name': 'Garcia', 'role': 'PROFESSOR'},
            {'username': 'prof.smith', 'email': 'smith@richwell.edu', 'first_name': 'John', 'last_name': 'Smith', 'role': 'PROFESSOR'},
        ]

        users = {}
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': user_data['role'],
                }
            )
            if created:
                user.set_password('password123')  # Default password for all test users
                user.save()
            users[user_data['role']] = users.get(user_data['role'], []) + [user]

        self.stdout.write(self.style.SUCCESS(f'  Created {len(users_data)} users'))
        return users

    def seed_courses(self):
        """Create academic programs/courses."""
        self.stdout.write('Seeding courses...')

        courses_data = [
            {
                'code': 'BSCS',
                'name': 'Bachelor of Science in Computer Science',
                'description': 'Four-year degree program focusing on software development, algorithms, and computer systems.',
                'total_units': 180
            },
            {
                'code': 'BSIT',
                'name': 'Bachelor of Science in Information Technology',
                'description': 'Four-year degree program specializing in IT infrastructure, networking, and system administration.',
                'total_units': 180
            },
            {
                'code': 'BSBA',
                'name': 'Bachelor of Science in Business Administration',
                'description': 'Four-year degree program covering business management, finance, and entrepreneurship.',
                'total_units': 180
            },
            {
                'code': 'BSAC',
                'name': 'Bachelor of Science in Accountancy',
                'description': 'Four-year degree program preparing students for careers in accounting and auditing.',
                'total_units': 180
            },
            {
                'code': 'BEED',
                'name': 'Bachelor of Elementary Education',
                'description': 'Four-year degree program for aspiring elementary school teachers.',
                'total_units': 180
            },
        ]

        courses = []
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults=course_data
            )
            courses.append(course)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(courses)} courses'))
        return courses

    def seed_subjects(self, courses):
        """Create subjects for each course."""
        self.stdout.write('Seeding subjects...')

        # Find BSCS course
        bscs = next((c for c in courses if c.code == 'BSCS'), None)
        bsit = next((c for c in courses if c.code == 'BSIT'), None)

        subjects_data = [
            # Computer Science Subjects - Year 1
            {'code': 'CS101', 'name': 'Introduction to Programming', 'description': 'Fundamentals of programming using Python', 'units': 3, 'course': bscs},
            {'code': 'CS102', 'name': 'Computer Fundamentals', 'description': 'Basic computer concepts and architecture', 'units': 3, 'course': bscs},
            {'code': 'MATH101', 'name': 'College Algebra', 'description': 'Algebraic concepts and problem solving', 'units': 3, 'course': bscs},
            {'code': 'ENG101', 'name': 'English Communication', 'description': 'Written and oral communication skills', 'units': 3, 'course': bscs},
            {'code': 'PE101', 'name': 'Physical Education 1', 'description': 'Basic physical fitness and health', 'units': 2, 'course': bscs},

            # Computer Science Subjects - Year 2
            {'code': 'CS201', 'name': 'Database Systems', 'description': 'Database design and SQL programming', 'units': 3, 'course': bscs},
            {'code': 'CS202', 'name': 'Data Structures and Algorithms', 'description': 'Advanced data structures and algorithm design', 'units': 3, 'course': bscs},
            {'code': 'CS203', 'name': 'Object-Oriented Programming', 'description': 'OOP concepts using Java', 'units': 3, 'course': bscs},
            {'code': 'MATH201', 'name': 'Discrete Mathematics', 'description': 'Mathematical foundations for CS', 'units': 3, 'course': bscs},

            # Computer Science Subjects - Year 3
            {'code': 'CS301', 'name': 'Web Development', 'description': 'Full-stack web development with modern frameworks', 'units': 3, 'course': bscs},
            {'code': 'CS302', 'name': 'Software Engineering', 'description': 'Software development lifecycle and methodologies', 'units': 3, 'course': bscs},
            {'code': 'CS303', 'name': 'Network Engineering', 'description': 'Computer networks and protocols', 'units': 3, 'course': bscs},
            {'code': 'CS304', 'name': 'Operating Systems', 'description': 'OS concepts and system programming', 'units': 3, 'course': bscs},

            # Computer Science Subjects - Year 4
            {'code': 'CS401', 'name': 'Algorithms and Complexity', 'description': 'Advanced algorithms and computational complexity', 'units': 3, 'course': bscs},
            {'code': 'CS402', 'name': 'Artificial Intelligence', 'description': 'AI concepts and machine learning basics', 'units': 3, 'course': bscs},
            {'code': 'CS403', 'name': 'Mobile App Development', 'description': 'iOS and Android development', 'units': 3, 'course': bscs},
            {'code': 'CS404', 'name': 'Capstone Project', 'description': 'Final year project', 'units': 6, 'course': bscs},

            # IT Subjects
            {'code': 'IT101', 'name': 'Introduction to IT', 'description': 'Overview of information technology', 'units': 3, 'course': bsit},
            {'code': 'IT201', 'name': 'Network Administration', 'description': 'Network setup and management', 'units': 3, 'course': bsit},
            {'code': 'IT301', 'name': 'System Administration', 'description': 'Server and system management', 'units': 3, 'course': bsit},
            {'code': 'IT401', 'name': 'IT Project Management', 'description': 'Managing IT projects', 'units': 3, 'course': bsit},
        ]

        subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            subjects.append(subject)

        # Set prerequisites
        prerequisites = {
            'CS201': ['CS101'],  # Database needs Programming
            'CS202': ['CS101'],  # Data Structures needs Programming
            'CS203': ['CS101'],  # OOP needs Programming
            'CS301': ['CS201', 'CS203'],  # Web Dev needs Database and OOP
            'CS302': ['CS203'],  # Software Eng needs OOP
            'CS401': ['CS202'],  # Algorithms needs Data Structures
            'CS402': ['CS202'],  # AI needs Data Structures
            'CS403': ['CS203'],  # Mobile Dev needs OOP
            'CS404': ['CS301', 'CS302'],  # Capstone needs Web Dev and SE
        }

        for subject_code, prereq_codes in prerequisites.items():
            subject = next((s for s in subjects if s.code == subject_code), None)
            if subject:
                for prereq_code in prereq_codes:
                    prereq = next((s for s in subjects if s.code == prereq_code), None)
                    if prereq:
                        subject.prerequisites.add(prereq)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(subjects)} subjects'))
        return subjects

    def seed_terms(self):
        """Create academic terms."""
        self.stdout.write('Seeding terms...')

        current_year = timezone.now().year
        terms_data = [
            {
                'name': f'1st Semester {current_year-1}-{current_year}',
                'academic_year': f'{current_year-1}-{current_year}',
                'semester': 'FIRST',
                'start_date': timezone.now().date() - timedelta(days=365),
                'end_date': timezone.now().date() - timedelta(days=180),
                'enrollment_start': timezone.now().date() - timedelta(days=380),
                'enrollment_end': timezone.now().date() - timedelta(days=350),
                'is_active': False,
            },
            {
                'name': f'2nd Semester {current_year-1}-{current_year}',
                'academic_year': f'{current_year-1}-{current_year}',
                'semester': 'SECOND',
                'start_date': timezone.now().date() - timedelta(days=180),
                'end_date': timezone.now().date() - timedelta(days=60),
                'enrollment_start': timezone.now().date() - timedelta(days=200),
                'enrollment_end': timezone.now().date() - timedelta(days=170),
                'is_active': False,
            },
            {
                'name': f'1st Semester {current_year}-{current_year+1}',
                'academic_year': f'{current_year}-{current_year+1}',
                'semester': 'FIRST',
                'start_date': timezone.now().date() - timedelta(days=30),
                'end_date': timezone.now().date() + timedelta(days=120),
                'enrollment_start': timezone.now().date() - timedelta(days=50),
                'enrollment_end': timezone.now().date() + timedelta(days=10),
                'is_active': True,
            },
        ]

        terms = []
        for term_data in terms_data:
            term, created = Term.objects.get_or_create(
                name=term_data['name'],
                defaults=term_data
            )
            terms.append(term)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(terms)} terms'))
        return terms

    def seed_students(self, users, courses):
        """Create student records."""
        self.stdout.write('Seeding students...')

        student_names = [
            ('Juan', 'Dela Cruz'), ('Maria', 'Santos'), ('Jose', 'Reyes'),
            ('Ana', 'Garcia'), ('Pedro', 'Lopez'), ('Sofia', 'Martinez'),
            ('Miguel', 'Hernandez'), ('Isabella', 'Gonzalez'), ('Carlos', 'Rodriguez'),
            ('Lucia', 'Fernandez'), ('Diego', 'Perez'), ('Valentina', 'Sanchez'),
            ('Alejandro', 'Ramirez'), ('Camila', 'Torres'), ('Sebastian', 'Flores'),
            ('Emma', 'Rivera'), ('Mateo', 'Gomez'), ('Olivia', 'Diaz'),
            ('Daniel', 'Cruz'), ('Mia', 'Ortiz'), ('Gabriel', 'Morales'),
            ('Sophia', 'Castro'), ('Lucas', 'Ramos'), ('Ava', 'Vargas'),
            ('Ethan', 'Herrera'), ('Charlotte', 'Mendoza'), ('Alexander', 'Silva'),
            ('Amelia', 'Medina'), ('Benjamin', 'Jimenez'), ('Harper', 'Ruiz'),
        ]

        students = []
        year_levels = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4]  # Distribution of year levels
        statuses = ['ACTIVE'] * 8 + ['PROBATION'] + ['LOA']

        for i, (first_name, last_name) in enumerate(student_names[:30], start=1):
            username = f'student{i:03d}'

            # Create user
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@student.richwell.edu',
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'STUDENT',
                }
            )
            if created:
                user.set_password('password123')
                user.save()

            # Create student
            student_id = f'2024-{i:05d}'
            year_level = year_levels[i % len(year_levels)]
            status = random.choice(statuses)
            course = random.choice(courses)

            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={
                    'user': user,
                    'course': course,
                    'year_level': year_level,
                    'status': status,
                    'enrollment_date': timezone.now().date() - timedelta(days=365 * (year_level - 1)),
                }
            )
            students.append(student)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(students)} students'))
        return students

    def seed_sections(self, subjects, terms, users):
        """Create class sections."""
        self.stdout.write('Seeding sections...')

        professors = []
        for role, role_users in users.items():
            if role == 'PROFESSOR':
                professors.extend(role_users)

        current_term = [t for t in terms if t.is_active][0]

        # Get current year subjects (1st and 2nd year for active term)
        active_subjects = [s for s in subjects if s.code.startswith('CS1') or s.code.startswith('CS2') or s.code.startswith('MATH') or s.code.startswith('ENG') or s.code.startswith('PE')][:15]

        sections = []
        section_letters = ['A', 'B', 'C']
        schedules = [
            ('MWF', '8:00 AM - 9:30 AM'),
            ('MWF', '9:00 AM - 10:30 AM'),
            ('MWF', '10:00 AM - 11:30 AM'),
            ('MWF', '1:00 PM - 2:30 PM'),
            ('MWF', '2:00 PM - 3:30 PM'),
            ('TTH', '8:00 AM - 9:30 AM'),
            ('TTH', '10:00 AM - 11:30 AM'),
            ('TTH', '1:00 PM - 2:30 PM'),
            ('TTH', '3:00 PM - 4:30 PM'),
        ]

        rooms = ['Room 301', 'Room 302', 'Room 303', 'Lab 101', 'Lab 102', 'Room 205', 'Room 402']

        for subject in active_subjects:
            for letter in section_letters[:2]:  # Create 2 sections per subject
                section_name = f'{subject.code}-{letter}'
                days, time = random.choice(schedules)

                section, created = Section.objects.get_or_create(
                    section_name=section_name,
                    term=current_term,
                    defaults={
                        'subject': subject,
                        'professor': random.choice(professors) if professors else None,
                        'schedule_days': days,
                        'schedule_time': time,
                        'room': random.choice(rooms),
                        'capacity': random.choice([30, 35, 40]),
                    }
                )
                sections.append(section)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(sections)} sections'))
        return sections

    def seed_enrollments(self, students, sections, terms):
        """Create student enrollments."""
        self.stdout.write('Seeding enrollments...')

        current_term = [t for t in terms if t.is_active][0]

        enrollments = []
        for student in students:
            # Enroll each student in 5-7 subjects
            num_subjects = random.randint(5, 7)
            student_sections = random.sample(sections, min(num_subjects, len(sections)))

            for section in student_sections:
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    section=section,
                    term=current_term,
                    defaults={
                        'enrollment_date': current_term.enrollment_start,
                        'status': 'ENROLLED',
                    }
                )
                enrollments.append(enrollment)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(enrollments)} enrollments'))
        return enrollments

    def seed_grades(self, enrollments):
        """Create grade records."""
        self.stdout.write('Seeding grades...')

        grades_pool = [1.00, 1.25, 1.50, 1.75, 2.00, 2.25, 2.50, 2.75, 3.00]

        # Grade 70% of enrollments, leave 30% pending
        enrollments_to_grade = random.sample(enrollments, int(len(enrollments) * 0.7))

        grades = []
        for enrollment in enrollments_to_grade:
            grade_value = random.choice(grades_pool)

            grade, created = GradeRecord.objects.get_or_create(
                enrollment=enrollment,
                defaults={
                    'grade': grade_value,
                    'remarks': 'Passed' if grade_value <= 3.00 else 'Failed',
                    'encoded_at': timezone.now(),
                }
            )
            grades.append(grade)

        self.stdout.write(self.style.SUCCESS(f'  Created {len(grades)} grade records'))
        return grades

    def print_summary(self):
        """Print summary of seeded data."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('DATABASE SEEDING SUMMARY'))
        self.stdout.write('='*60)

        summary = [
            ('Users', User.objects.count()),
            ('  - Admins', User.objects.filter(role='ADMIN').count()),
            ('  - Deans', User.objects.filter(role='DEAN').count()),
            ('  - Registrars', User.objects.filter(role='REGISTRAR').count()),
            ('  - Admission', User.objects.filter(role='ADMISSION').count()),
            ('  - Professors', User.objects.filter(role='PROFESSOR').count()),
            ('  - Students', User.objects.filter(role='STUDENT').count()),
            ('Courses', Course.objects.count()),
            ('Subjects', Subject.objects.count()),
            ('Terms', Term.objects.count()),
            ('  - Active', Term.objects.filter(is_active=True).count()),
            ('Students', Student.objects.count()),
            ('Sections', Section.objects.count()),
            ('Enrollments', Enrollment.objects.count()),
            ('Grades', GradeRecord.objects.count()),
        ]

        for label, count in summary:
            self.stdout.write(f'{label:<20} {count:>5}')

        self.stdout.write('='*60 + '\n')

    def print_credentials(self):
        """Print login credentials for testing."""
        self.stdout.write(self.style.SUCCESS('TEST CREDENTIALS'))
        self.stdout.write('='*60)
        self.stdout.write('All passwords: password123\n')

        credentials = [
            ('ADMIN', 'admin', 'System Administrator'),
            ('DEAN', 'dean.cs', 'Robert Mitchell'),
            ('REGISTRAR', 'registrar1', 'Maria Rodriguez'),
            ('ADMISSION', 'admission1', 'Emily Johnson'),
            ('PROFESSOR', 'prof.johnson', 'Michael Johnson'),
            ('STUDENT', 'student001', 'Juan Dela Cruz'),
        ]

        for role, username, name in credentials:
            self.stdout.write(f'{role:<12} {username:<15} ({name})')

        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('\nYou can now login at: http://127.0.0.1:8000/'))
        self.stdout.write('='*60 + '\n')
