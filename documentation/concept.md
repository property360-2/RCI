# 🧩 Richwell College Portal v3.0 — Concept & Plan

### (Django + DRF + HTMX + Tailwind CDN)

---

## 1 ) Product Overview

A modular, **archive-first academic portal** covering enrollment, grade encoding, transferee mapping, section / curriculum management, and student analytics.
Every record uses **soft-archive** (no deletes).

**Core Principles**

* Archive + restore instead of delete
* Role-based access across departments
* Full audit trail for all changes
* Atomic template components for consistent UI
* CDN-served static / media assets

---

## 2 ) Roles & Scope

| Role          | Core Functions                                       | Archive Access |
| ------------- | ---------------------------------------------------- | -------------- |
| **Dean**      | Courses / Subjects / Sections / Professors / Prereqs | Full + restore |
| **Registrar** | INC confirmation / Student archives / Transferees    | Partial        |
| **Admission** | Enrollment intake / Advising (read-only sections)    | None           |
| **Professor** | Grade encoding / INC resolution                      | None           |
| **Student**   | View grades / records / analytics                    | None           |

System flow → **Dean → Admission → Registrar → Professor → Student**

---

## 3 ) Architecture

### 3.1 Backend Apps

```
backend/
├─ config/          # settings, urls, wsgi/asgi
├─ core/            # mixins, utils, permissions
├─ users/           # auth, roles, profiles
├─ students/        # student profiles, docs
├─ courses/         # programs, curricula
├─ subjects/        # subjects, prereqs
├─ sections/        # sections, professor assign
├─ enrollments/     # student–subject link
├─ grades/          # grade encoding, INC
├─ terms/           # school years, semesters
├─ archive/         # archive / restore
└─ audit/           # audit trail
```

### 3.2 Core Mixins

```python
class ArchiveMixin(models.Model):
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    class Meta: abstract = True

class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True
```

### 3.3 Database Notes

* `students.documents`: JSON field (future-ready for Cloudinary/S3)
* `section_id` nullable → handles irregular / transferees
* 30-unit cap enforced at service layer

---

## 4 ) Models (Outline)

**Academics**

* `Term`: `school_year`, `semester`, `active`
* `Course`, `Subject`, `Section`, `AssignedSubject`
* `SubjectPrereq`: M2M link

**Students & Enrollment**

* `Student`: Archive + TimeStamp + JSON docs
* `Enrollment`: Archive + unit cap + nullable section

**Grades & INC**

* `GradeRecord`: grade choice (1.0 … 3.0, INC)
* `INCRecord`: deadline / resolved_at / note

**AuditTrail**

```python
class AuditTrail(models.Model):
    actor = models.ForeignKey('users.User', on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    table_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

## 5 ) Permissions & Policies

| Feature           | Dean                   | Registrar   | Admission  | Professor         | Student |
| ----------------- | ---------------------- | ----------- | ---------- | ----------------- | ------- |
| Courses/Subjects  | CRUD + archive/restore | R           | R          | R                 | R       |
| Sections          | CRUD + archive/restore | R           | R          | R                 | R       |
| Assigned Subjects | CRUD                   | R           | R          | R                 | R       |
| Enrollment Intake | R                      | R           | **Create** | R                 | R       |
| Grade Encoding    | R                      | Approve INC | R          | **Create/Update** | R       |
| Archive Toggle    | **Full**               | Partial     | –          | –                 | –       |

**INC Deadlines:** 6 mo (minor), 12 mo (major) → auto expire via cron
**Unit Cap:** ≤ 30 units → reject above cap (422)

---

## 6 ) API Key Endpoints (DRF)

```
/auth/login/ (JWT)
 /auth/refresh/
/users/me/
/terms/ (list + create)
 /courses/, /subjects/ (list / CRUD / archive / restore)
/sections/ (list / create / assign-professor)
/enrollments/ (create / my)
/grades/ (encode / inc / resolve)
/archive/ (restore/<model>/<id>/)
/audit/ (logs)
```

Filter `archived=false` by default; toggle with `?archived=true`.

---

## 7 ) Frontend — Atomic Django Templates + HTMX

```
templates/
├─ atoms/
│  ├─ button.html
│  ├─ input.html
│  ├─ badge.html
│  ├─ modal.html
│  └─ tooltip.html
├─ molecules/
│  ├─ login_form.html
│  ├─ search_bar.html
│  ├─ confirm_modal.html
│  └─ stats_tile.html
├─ organisms/
│  ├─ navbar.html
│  ├─ sidebar.html
│  ├─ section_table.html
│  ├─ enrollment_panel.html
│  └─ grade_table.html
├─ layouts/
│  ├─ dashboard.html
│  ├─ auth.html
│  └─ archive.html
└─ pages/
   ├─ dean/
   ├─ registrar/
   ├─ admission/
   ├─ professor/
   └─ student/
```

**HTMX Usage**

* Inline archive / restore actions
* Modal confirmations (`hx-get`, `hx-post`)
* Pagination / search filters (`hx-target`)
* Grade encoding forms (submit w/o reload)
* Slot updates in enrollment table

**Tailwind UI Guide**

* Light mode only (`bg-white`, `bg-gray-50`)
* Buttons: `blue`, `gray`, `red`
* Rounded cards, soft shadows, ample spacing

---

## 8 ) Static & Media (CDN)

* `django-storages` + Cloudinary or S3
* Versioned URLs + long-term cache
* `ManifestStaticFilesStorage` for hashed files
* `collectstatic` → CDN bucket

---

## 9 ) Environment & Settings

`.env`

```
SECRET_KEY=
DB_URL=
ALLOWED_HOSTS=portal.richwell.edu
CORS_ALLOWED_ORIGINS=https://portal.richwell.edu
JWT_SECRET=
CLOUDINARY_URL=
CDN_URL=https://cdn.richwell.edu
```

Django settings:

* DRF pagination, throttling
* `CORS_ALLOW_CREDENTIALS=True`
* `SECURE_PROXY_SSL_HEADER` / `CSRF_TRUSTED_ORIGINS`

---

## 10 ) 📌 System Workflows (End-to-End)

### 🟣 Dean – Academic Setup

```
Create Term → Courses → Subjects → Prereqs → Sections → Assign Professors
```

After setup → Admission can enroll students; Professors see assigned sections.

### 🔵 Admission – Enrollment

```
Lookup/Create Student → Load eligible subjects → Validate prereqs + units → Confirm → Create enrollments → Slots decrement
```

Atomic slot decrement (`SELECT … FOR UPDATE`); audit log created; 30-unit limit enforced.

### 🟡 Professor – Grading / INC

```
Open section → Encode grade → Audit entry  
IF INC → Create INCRecord (deadline) → Registrar confirms resolution / auto-expire
```

### 🔴 Archive + Restore (Dean)

```
Archive record → hidden from default queries → accessible via ?archived=true → restore any time
```

### 🟤 Audit Trail

| Action     | Logged               | Content        |
| ---------- | -------------------- | -------------- |
| Create     | action=create        | new value      |
| Update     | action=update        | old + new      |
| Archive    | action=archive       | previous state |
| Restore    | action=restore       | restored state |
| INC expire | action=policy_expire | system actor   |

### 🔐 JWT Auth Flow (A)

```
login → access + refresh cookies → refresh rotates tokens → logout clears cookies
```

### 🟢 Analytics

```
Grades + Enrollments → aggregate endpoints → HTMX chart partials
```

Endpoints:
`/analytics/grades/distribution`, `/analytics/passfail`, `/analytics/inc/summary`

---

## 11 ) Non-Functional Requirements

* p95 < 300 ms for list endpoints
* Sentry error tracking + request logging
* Nightly DB backup (7/30 retention)
* JWT rotation, 2FA optional
* Target capacity: 5 k students / term

---

## 12 ) Development Phases (6–8 weeks)

### Phase 0 – Bootstrap (Day 0–1)

* Django project init
* Core apps (`core`, `users`, `audit`, `archive`)
* Env split (base/dev/prod)
* Tailwind CDN + HTMX wired
* Health endpoint (`/healthz`)
  ✅ Deliverable: project runs locally, CDN static working

### Phase 1 – Auth & Roles (Week 1)

* User model w/ `role` enum
* JWT (SimpleJWT) + blacklist
* `/auth/login`, `/auth/refresh`, `/users/me`
* Login template (Tailwind form + HTMX errors)
  ✅ Each role logs in / restricted properly

### Phase 2 – Academic Skeleton (Week 2)

* Apps: `terms`, `courses`, `subjects`, `sections`
* Models + ArchiveMixin + TimeStampMixin
* CRUD views + HTMX partials
  ✅ Dean creates subjects/sections + assigns professors

### Phase 3 – Enrollment (Week 3)

* App: `enrollments`
* 30-unit limit + atomic slot update
* Admission Kiosk template (HTMX modal confirm)
  ✅ Admission enrolls students; slots update live

### Phase 4 – Grades & INC (Week 4)

* `grades` app + INC policy cron
* Professor grade encode HTMX form
* Registrar INC resolution view
  ✅ Audit entries + deadline enforcement

### Phase 5 – Archive & Audit (Week 5)

* `/archive/<model>/<id>/restore`
* Audit middleware (saves diffs)
* Archive toggle in HTMX tables
  ✅ Dean restores; Registrar views archived records

### Phase 6 – Analytics (Week 6)

* Lightweight aggregate queries
* Charts (Chart.js via HTMX partials)
  ✅ Dashboards show live stats per role

### Phase 7 – Polish & Launch (Week 7–8)

* CSRF, rate limits, JWT rotation
* UI polish (light mode)
* Backup/restore scripts
* Docs + UAT sign-off

---

## 13 ) Testing & QA

* Unit tests ≥ 80 % coverage
* DRF API tests (Pytest)
* HTMX integration tests (Django TestClient)
* Factory data (factory_boy)
* `seed_demo` command for fixtures

---

## 14 ) Deployment

* Gunicorn + Nginx
* Static → CDN via `collectstatic`
* DB migrations + health check
* Rollback = previous build + DB backup

---

## 15 ) Branching & Releases

* `main` (protected) / `develop` (integration) / feature branches → PRs
* Tags `v0.x.y` per phase
* `CHANGELOG.md` required

---

## 16 ) Next Actions

1. Initialize repo (`backend/` only)
2. Add `ArchiveMixin`, `AuditTrail`, `User.role`
3. Implement JWT login + roles
4. Start Phase 2 (Academics CRUD + HTMX UI)

---
