# Richwell College Portal v3.0 - User Guide

Complete user guide for all roles in the Richwell College Portal academic management system.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Login & Authentication](#login--authentication)
3. [Dean Dashboard](#dean-dashboard)
4. [Registrar Dashboard](#registrar-dashboard)
5. [Admission Officer Dashboard](#admission-officer-dashboard)
6. [Professor Dashboard](#professor-dashboard)
7. [Student Dashboard](#student-dashboard)
8. [Common Features](#common-features)
9. [FAQs](#faqs)

---

## Getting Started

### System Overview

The Richwell College Portal is a web-based academic management system designed to streamline:
- **Enrollment Management** - Student registration and course enrollment
- **Grade Management** - Grade encoding and tracking
- **Academic Records** - Student transcripts and archives
- **Analytics** - Academic performance insights

### User Roles

The portal has **6 distinct roles**, each with specific permissions:

| Role | Primary Responsibilities | Access Level |
|------|-------------------------|--------------|
| **DEAN** | Academic oversight, analytics, strategic planning | Full read access to all data |
| **REGISTRAR** | Student records, enrollment management, archives | Full read/write for students, enrollments, grades |
| **ADMISSION** | New student processing, enrollment creation | Create students, create enrollments |
| **PROFESSOR** | Grade encoding, section management | Access to assigned sections only |
| **STUDENT** | View grades, view enrollments | Read-only access to own data |
| **ADMIN** | System administration | Full system access |

### Accessing the Portal

1. Open your web browser
2. Navigate to: **https://portal.richwell.edu** (or your institution's URL)
3. You'll be redirected to the login page

---

## Login & Authentication

### First-Time Login

1. On the login page, enter your **username** and **password**
2. Click **Sign In**
3. You'll be redirected to your role-specific dashboard

**Demo Quick Access:** The login page has quick-access buttons (Dean, Registrar, Admission, Professor) to pre-fill the username field for testing.

### Remember Me Feature

- Check the **"Remember me"** box to stay logged in for 2 weeks
- Unchecked: Session expires when browser closes
- Recommended for personal devices only

### Password Security

- **Minimum Length:** 8 characters
- **Requirements:** Mix of letters, numbers, and symbols
- **Change Password:** Available in Profile settings (Coming Soon)

### Troubleshooting Login Issues

**"Invalid username or password"**
- Verify username is correct (case-sensitive)
- Ensure Caps Lock is off
- Contact IT Support if password forgotten

**"Account Inactive"**
- Your account may be archived
- Contact the Registrar or IT Support

**"Session Expired"**
- Your session timed out due to inactivity
- Simply log in again

---

## Dean Dashboard

**Access Level:** Full read access to all academic data

### Overview

The Dean Dashboard provides high-level analytics and oversight of the entire academic institution.

### Key Features

#### 1. Academic Statistics

View real-time metrics:
- **Total Students:** Currently enrolled students
- **Total Courses:** Active degree programs
- **Faculty Members:** Active professors
- **Active Sections:** Sections offered this term

#### 2. Academic Management

Navigate to:
- **Courses:** View all degree programs (BSCS, BSBA, etc.)
- **Subjects:** Browse all subjects across programs
- **Sections:** See all sections being offered
- **Students:** Access student directory

#### 3. Analytics & Reports

Access comprehensive analytics:
- **Enrollment Trends:** Track enrollment over time
- **Grade Distribution:** View grade statistics by course/subject
- **Student Performance:** Identify at-risk students
- **Faculty Load:** Monitor professor assignments

#### 4. Archive Access

View archived records:
- Graduated students
- Completed terms
- Historical grade data
- **Note:** Dean can view but not modify archived data

### Common Tasks

**View Student Performance by Course:**
1. Click **Analytics** in navbar
2. Select **Grade Distribution**
3. Filter by course (e.g., BSCS)
4. View charts and statistics

**Check Faculty Assignments:**
1. Click **Academic Management**
2. Select **Sections**
3. Filter by term and professor
4. Export to PDF if needed

**Access Historical Data:**
1. Navigate to **Students** or **Enrollments**
2. Enable **"Show Archived"** toggle
3. Browse historical records
4. Use date filters to narrow results

---

## Registrar Dashboard

**Access Level:** Full read/write for students, enrollments, grades, archives

### Overview

The Registrar Dashboard is the command center for student records and enrollment management.

### Key Features

#### 1. Student Records Management

Comprehensive student database:
- **View Students:** Search, filter, and sort all students
- **Edit Records:** Update student information
- **Archive Students:** Soft-delete graduated/withdrawn students
- **Restore Students:** Recover archived records

#### 2. Enrollment Management

Control student enrollments:
- **Create Enrollments:** Enroll students in sections
- **Edit Enrollments:** Modify existing enrollments
- **30-Unit Cap Enforcement:** System prevents overloading
- **Prerequisite Checking:** Automatic validation

#### 3. Grade Records

Oversee all grades:
- **View All Grades:** Access to all grade records
- **Edit Grades:** Modify grades if needed (audit logged)
- **INC Management:** Track incomplete grades and deadlines
- **Grade Verification:** Approve professor-submitted grades

#### 4. Archive Management

Full archive control:
- **Archive Students:** Move graduated students to archive
- **Archive Enrollments:** Archive past term enrollments
- **Restore Records:** Recover mistakenly archived data
- **Bulk Operations:** Archive multiple records at once

### Common Tasks

**Enroll a Student in Sections:**
1. Navigate to **Enrollments** → **Create New**
2. Select the **Student** (search by name or ID)
3. Select the **Term** (e.g., Fall 2024)
4. Add **Sections** (system checks prerequisites and unit cap)
5. Review total units (must be ≤ 30 units)
6. Click **Submit Enrollment**
7. Confirmation email sent to student

**Archive a Graduated Student:**
1. Navigate to **Students**
2. Search for the student
3. Click **Actions** → **Archive Student**
4. Enter reason: "Graduated - Class of 2024"
5. Confirm archival
6. Student moved to archive (recoverable if needed)

**Fix a Grade Error:**
1. Navigate to **Grades**
2. Search by student name and subject
3. Click **Edit Grade**
4. Update grade value
5. Enter **Reason for Change** (mandatory for audit)
6. Click **Save**
7. System logs change with timestamp and user

**Generate Transcript:**
1. Navigate to **Students**
2. Select student
3. Click **Generate Transcript**
4. Choose **Unofficial** or **Official** (official has seal)
5. Download PDF
6. Print or email to student

---

## Admission Officer Dashboard

**Access Level:** Create students, create enrollments, read-only for other data

### Overview

The Admission Officer Dashboard streamlines new student onboarding and first-time enrollment.

### Key Features

#### 1. Applicant Management

Track prospective students:
- **Applicant Queue:** List of pending applications
- **Application Review:** Approve/reject applications
- **Document Verification:** Check submitted requirements
- **Status Tracking:** Monitor application progress

#### 2. Quick Enrollment

Fast-track new student setup:
- **Create Student Profile:** One-click student creation
- **Auto-Generate ID:** System assigns student number
- **Initial Enrollment:** Enroll in first-term subjects
- **Welcome Email:** Automated notification to student

#### 3. Enrollment Statistics

Monitor admission metrics:
- **Applications by Course:** Track program popularity
- **Enrollment Rate:** Acceptance vs. actual enrollment
- **First-Year Enrollment:** New student count per term
- **Course Capacity:** Available slots by program

### Common Tasks

**Process a New Student Application:**
1. Go to **Applicants** → **Pending Applications**
2. Click on applicant name to view details
3. Review:
   - High school grades
   - Entrance exam scores
   - Submitted documents
4. Click **Approve** or **Reject**
5. If approved, system creates student profile

**Quick Enroll a New Student:**
1. Select newly created student from dropdown
2. Choose **Course** (e.g., BSCS)
3. Choose **Term** (e.g., Fall 2024)
4. System auto-suggests 1st year subjects
5. Review suggested sections (balanced schedule)
6. Click **Enroll Student**
7. Welcome email sent with credentials

**Track Enrollment Progress:**
1. Navigate to **Dashboard** → **Enrollment Stats**
2. View charts:
   - Applications by course
   - Enrollment trends by term
   - Conversion rate (applied → enrolled)
3. Export reports for dean/registrar

---

## Professor Dashboard

**Access Level:** Manage assigned sections, encode grades, view student rosters

### Overview

The Professor Dashboard focuses on grade management and class section oversight.

### Key Features

#### 1. My Sections

View assigned teaching load:
- **Current Sections:** Classes you're teaching this term
- **Section Details:** Student roster, schedule, room
- **Enrollment Count:** Number of students per section
- **Subject Info:** Subject code, name, units

#### 2. Grade Encoding

Submit student grades:
- **Grade Entry:** Input grades for enrolled students
- **Grade Scale:** 5.0 (highest) to 1.0 (failed), INC (incomplete)
- **INC Deadline:** Set completion deadline for incompletes
- **Bulk Import:** Upload grades via CSV
- **Submit for Review:** Send to registrar for approval

#### 3. Student Roster

Access class lists:
- **View Roster:** List of enrolled students
- **Student Details:** Name, ID, course, year level
- **Attendance Tracking:** Mark present/absent (Coming Soon)
- **Export Roster:** Download as PDF or Excel

#### 4. INC Management

Track incomplete grades:
- **Active INCs:** Students with incomplete grades
- **Deadline Tracking:** View conversion deadlines
- **Convert INC:** Change INC to final grade
- **Expiration Alerts:** Notification before deadline

### Common Tasks

**Encode Final Grades:**
1. Navigate to **Grade Encoding**
2. Select your **Section** (e.g., COMP101-A Fall 2024)
3. Grade entry table appears with student list
4. For each student:
   - Enter grade (1.0-5.0)
   - Or select **INC** if incomplete
5. If INC selected, set **Completion Deadline**
6. Click **Save Draft** (saves but doesn't submit)
7. Review grades carefully
8. Click **Submit to Registrar**
9. Confirmation message displayed

**Convert an INC Grade:**
1. Navigate to **My Sections** → **INC Tracking**
2. Find student with INC grade
3. Click **Convert INC**
4. Enter final grade (1.0-5.0)
5. Add notes explaining completion
6. Click **Submit**
7. Registrar receives notification

**Download Student Roster:**
1. Navigate to **My Sections**
2. Click on section name
3. Click **Download Roster**
4. Choose format: **PDF** (for printing) or **Excel** (for editing)
5. File downloads to your computer

---

## Student Dashboard

**Access Level:** View own grades, view own enrollments, read-only

### Overview

The Student Dashboard provides personal academic information and tools.

### Key Features

#### 1. My Grades

View academic performance:
- **Current Term Grades:** Grades for ongoing classes
- **Grade History:** All past grades by term
- **GPA Calculation:** Cumulative and term GPA
- **Grade Breakdown:** Performance by subject
- **INC Tracking:** Incomplete grades and deadlines

#### 2. My Enrollments

Track course enrollments:
- **Current Enrollments:** Sections enrolled this term
- **Schedule View:** Class times and rooms
- **Unit Count:** Total units enrolled (max 30)
- **Enrollment History:** Past term enrollments

#### 3. Academic Standing

Monitor academic progress:
- **Required Units:** Progress toward graduation
- **Completed Units:** Units earned so far
- **Remaining Units:** Units needed to graduate
- **Prerequisite Tracking:** Subjects unlocked for next term

#### 4. Enrollment Actions

(Coming Soon)
- **Add/Drop:** Modify enrollments during add/drop period
- **Waitlist:** Join waitlist for full sections
- **Evaluation:** Rate professors and subjects

### Common Tasks

**View Current Grades:**
1. Login to portal
2. Dashboard shows grade summary cards
3. Click **My Grades** for detailed view
4. Select term from dropdown
5. View grades by subject:
   - Subject code and name
   - Professor name
   - Grade received
   - Status (PASSED, FAILED, INC)

**Check Enrollment Status:**
1. Navigate to **My Enrollments**
2. Current term enrollment shows:
   - Section name
   - Schedule (days and time)
   - Room number
   - Professor
3. Total units displayed at top
4. View schedule in calendar format

**Track Academic Progress:**
1. Navigate to **Academic Standing**
2. View progress bar:
   - Blue: Completed units
   - Gray: Remaining units
3. See breakdown:
   - **Total Required:** 120 units (for BSCS)
   - **Completed:** 45 units
   - **Remaining:** 75 units
4. View next available subjects (prerequisites met)

**Download Transcript:**
1. Navigate to **Profile** → **Documents**
2. Click **Request Transcript**
3. Choose type:
   - **Unofficial:** Free, instant download
   - **Official:** $10 fee, sealed, mailed
4. For official: Fill payment form
5. Download PDF (unofficial) or await mail (official)

---

## Common Features

### Navigation

#### Top Navbar
- **Dashboard:** Return to home dashboard
- **Role-Specific Links:** Quick access to main features
- **Notifications:** Bell icon (Coming Soon)
- **Profile Dropdown:** Access profile and logout

#### Sidebar (Desktop)
- **Collapsible:** Click arrow to expand/collapse
- **Persistent State:** Sidebar state saved in browser
- **Role-Specific Menu:** Shows relevant menu items only

#### Mobile Navigation
- **Hamburger Menu:** Tap to open mobile menu
- **Full-Screen Menu:** Overlay with all navigation items
- **Tap Outside to Close:** Click anywhere to close

### Search & Filtering

#### Search Bar
- **Global Search:** Search students, courses, subjects
- **Autocomplete:** Suggestions as you type
- **Quick Results:** Instant results without page reload

#### Filters
- **Date Range:** Filter by term, semester, year
- **Status Filter:** Active, archived, all
- **Role Filter:** Filter by user role (Dean/Registrar only)
- **Export:** Export filtered results to CSV/PDF

### Notifications (Coming Soon)

- **Bell Icon:** Shows unread notification count
- **Notification Types:**
  - Grade posted
  - Enrollment confirmed
  - INC deadline approaching
  - System announcements
- **Mark as Read:** Click to dismiss
- **View All:** Link to notification history

### Profile Management

#### View Profile
1. Click **profile avatar** in top-right
2. Select **My Profile**
3. View your information:
   - Name, email, role
   - Last login time
   - Account created date

#### Edit Profile (Coming Soon)
- Update personal information
- Change password
- Upload profile picture
- Set notification preferences

### Logout

1. Click **profile avatar** in top-right
2. Select **Sign Out**
3. Confirmation message displayed
4. Redirected to login page

---

## FAQs

### General

**Q: Can I access the portal on mobile?**
A: Yes, the portal is fully responsive and works on all devices.

**Q: What browsers are supported?**
A: Chrome, Firefox, Safari, Edge (latest versions).

**Q: How do I reset my password?**
A: Contact IT Support. Self-service password reset coming soon.

### Students

**Q: When can I view my grades?**
A: Grades are visible after professors submit and registrar approves them.

**Q: Why can't I enroll in a subject?**
A: Check if:
- You've met prerequisites
- You haven't exceeded 30-unit cap
- Section isn't full
- Enrollment period is open

**Q: What does INC mean?**
A: INC (Incomplete) means you need to complete requirements. Check deadline with professor.

**Q: How do I get a transcript?**
A: Request in your dashboard under Profile → Documents.

### Professors

**Q: Can I edit grades after submission?**
A: Contact the registrar. All grade changes are audited.

**Q: What if a student isn't on my roster?**
A: Student may have dropped or enrolled late. Check with registrar.

**Q: How do I set an INC deadline?**
A: When encoding grades, select INC and enter deadline (max 1 year from term end).

### Registrar/Admission

**Q: Can I archive multiple students at once?**
A: Yes, select multiple students and use bulk archive action.

**Q: How do I restore an archived record?**
A: Navigate to archive view, find record, click Restore.

**Q: What happens when I archive a student?**
A: Student is hidden from active views but data is preserved. Can be restored anytime.

---

## Support & Feedback

### Getting Help

- **IT Support:** it-support@richwell.edu
- **Phone:** +1 (555) 123-4567
- **Office Hours:** Mon-Fri 8AM-5PM
- **GitHub Issues:** Report bugs at repository

### Feature Requests

Submit feature requests through:
1. IT Support email
2. GitHub Issues (mark as "enhancement")
3. Monthly feedback surveys

### Training Sessions

Free training available:
- **New User Orientation:** First Monday of each month
- **Role-Specific Training:** By appointment
- **Video Tutorials:** Available on portal homepage

---

**Last Updated:** 2024
**Version:** 3.0
**For:** All Portal Users
**Maintained by:** Richwell College IT Team
