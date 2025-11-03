### Phase 0 — Project Bootstrap (Day 0–1)

* Repos (backend/frontend), Docker compose, settings split (`base/dev/prod`), `.env` templates
* CDN/static/media config (Cloudinary or S3), CI (ruff/black/pytest), pre-commit
* **Deliverable:** `/healthz` up, collectstatic to CDN, CI green
* **Acceptance:** One-command local up; PRs auto-test

### Phase 1 — Auth & Roles (Week 1)

* `User` (extends `AbstractUser`) with `role`, JWT (simplejwt), DRF permissions
* Endpoints: `/auth/login`, `/auth/refresh`, `/users/me`
* Frontend atoms + LoginForm + route guard
* **Deliverable:** Tag `v0.1.0`
* **Acceptance:** Role-based routing works; tests pass

### Phase 2 — Academic Skeleton (Week 2)

* Apps: `terms`, `courses`, `subjects`, `sections` (+ `ArchiveMixin`, `TimeStampMixin`)
* Endpoints: CRUD + assign professor + slot capacity; `archived=false` default, toggle for privileged
* Dean dashboard basics (create subjects/sections)
* **Deliverable:** Tag `v0.2.0`
* **Acceptance:** Dean can create course/subject/section and assign professor

### Phase 3 — Enrollment Workflow (Week 3)

* `enrollments` app; prereq check; **30-unit cap**; atomic slot decrement
* Endpoints: POST `/enrollments` (Admission), GET `/enrollments/my` (Student)
* Admission Kiosk page (New/Current/Transferee → confirm modal)
* **Deliverable:** Tag `v0.3.0`
* **Acceptance:** Enrollment succeeds; slots reduce; student sees schedule

### Phase 4 — Grades & INC (Week 4)

* `grades` + `inc_records`; encode (choices: 1.0…3.0, INC); INC resolve (Professor → Registrar)
* Cron/management command: INC expiry (Minor 6 mo, Major 12 mo)
* Grade table + INC panel UI
* **Deliverable:** Tag `v0.4.0`
* **Acceptance:** Encode + resolve works; expired INC auto-marked

### Phase 5 — Archive & Audit (Week 5)

* POST `/archive/<model>/<id>/restore` (Dean); audit diffs (old/new JSON)
* Archive toggles, Audit Log viewer
* **Deliverable:** Tag `v0.5.0`
* **Acceptance:** Restore verified; Registrar can view archived students/enrollments

### Phase 6 — Analytics & Dashboards (Week 6)

* Lightweight endpoints: grade distribution, pass/fail, INC summary, GPA trend
* Role dashboards (Dean/Registrar/Professor/Student) with charts
* **Deliverable:** Tag `v0.6.0`
* **Acceptance:** Charts accurate vs seeded data; p95 < 300ms

### Phase 7 — Polish, Security & Launch (Weeks 7–8)

* Hardening: rate limits, JWT rotation, 2FA opt, CORS/CSRF, Sentry
* Theming polish (light mode, purple/yellow), a11y pass, docs (OpenAPI, SOPs)
* Backups + rollback; blue/green deploy
* **Deliverable:** Tag `v1.0.0`
* **Acceptance:** UAT sign-off + rollback documented

**Cross-cutting DoD**

* Tests ≥ 80% on changed lines; audit on all mutations; archive toggle respected; CI green; seeds updated.
