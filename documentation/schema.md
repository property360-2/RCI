

# 🧩 **Richwell College Portal v3.0 – Database Schema (Markdown)**

| **Table Name**         | **Purpose / Description**                                                    | **Key Fields**                                                                                             | **Relationships   / References**                                                                                  | **Archive Enabled** |
| ---------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------- |
| **users**              | Stores all system accounts (Dean, Registrar, Admission, Professor, Student). | `id`, `username`, `password`, `role`, `is_active`                                                          | One-to-one with `students`; foreign key for `audit_trail.archived_by` and `archived_by` fields in other tables. | ✅                  |
| **students**           | Holds student profiles and document info.                                    | `id`, `user_id`, `course_id`, `documents (JSON)`, `status`                                                 | FK → `users`, FK → `courses`; One-to-many → `enrollments`.                                                      | ✅                  |
| **courses**            | Represents degree programs (BSIT, BSEd, etc.).                               | `id`, `code`, `title`, `description`                                                                       | One-to-many → `subjects`, `sections`, `students`.                                                               | ✅                  |
| **subjects**           | Academic subjects tied to a course.                                          | `id`, `code`, `title`, `units`, `subject_type`                                                             | FK → `courses`; M2M → self via `prerequisites`; One-to-many → `enrollments`.                                    | ✅                  |
| **prerequisites**      | Maps prerequisite subjects.                                                  | `id`, `subject_id`, `prerequisite_id`                                                                      | Both FKs → `subjects`.                                                                                          | ❌                  |
| **school_terms**       | Tracks academic years and semesters.                                         | `id`, `school_year`, `semester`, `active`                                                                  | One-to-many → `sections`, `enrollments`.                                                                        | ❌                  |
| **sections**           | Groupings of students under a course and term.                               | `id`, `code`, `course_id`, `term_id`, `professor_id`, `capacity`, `slots_remaining`                        | FK → `courses`, `school_terms`, `users (professor)`; One-to-many → `assigned_subjects`, `enrollments`.          | ✅                  |
| **assigned_subjects**  | Links subjects to professors and sections.                                   | `id`, `section_id`, `subject_id`, `professor_id`                                                           | FK → `sections`, `subjects`, `users (professor)`.                                                               | ✅                  |
| **enrollments**        | Core record of student-to-subject linkage.                                   | `id`, `student_id`, `subject_id`, `section_id`, `term_id`, `units`, `status`                               | FK → `students`, `subjects`, `sections`, `school_terms`; One-to-one → `grade_records`, `inc_records`.           | ✅                  |
| **grade_records**      | Stores final encoded grades per enrollment.                                  | `id`, `enrollment_id`, `grade`, `encoded_by`, `encoded_at`                                                 | One-to-one → `enrollments`; FK → `users (professor)`.                                                           | ✅                  |
| **inc_records**        | Tracks incomplete subjects and resolution.                                   | `id`, `enrollment_id`, `deadline`, `resolved_at`, `resolution_note`, `confirmed_by`                        | One-to-one → `enrollments`; FK → `users (registrar)`.                                                           | ✅                  |
| **audit_trail**        | Logs all CRUD + archive actions.                                             | `id`, `actor_id`, `action`, `table_name`, `record_id`, `old_value (JSON)`, `new_value (JSON)`, `timestamp` | FK → `users (actor)`                                                                                            | ❌                  |
| **archive (mixin)**    | Inherited by multiple tables.                                                | `archived`, `archived_at`, `archived_by`                                                                   | FK → `users (Dean/Registrar)`                                                                                   | ✅                  |
| **timestamps (mixin)** | Auto timestamping for all models.                                            | `created_at`, `updated_at`                                                                                 | —                                                                                                               | ✅ (inherited)      |

---

## 🧠 **Relationships Overview**

| **From**       | **To**                             | **Type**            | **Description**                                        |
| -------------- | ---------------------------------- | ------------------- | ------------------------------------------------------ |
| `users`        | `students`                         | One-to-One          | Each student has a linked user account.                |
| `courses`      | `subjects`, `sections`, `students` | One-to-Many         | Course owns multiple subjects, sections, and students. |
| `subjects`     | `prerequisites`                    | Many-to-Many (self) | Each subject can depend on multiple others.            |
| `sections`     | `assigned_subjects`                | One-to-Many         | A section can have multiple assigned subjects.         |
| `sections`     | `enrollments`                      | One-to-Many         | Each enrollment links a student to a section.          |
| `enrollments`  | `grade_records`                    | One-to-One          | Each enrollment has one grade record.                  |
| `enrollments`  | `inc_records`                      | One-to-One          | Each enrollment may have one INC record.               |
| `school_terms` | `sections`, `enrollments`          | One-to-Many         | Organizes data by term and semester.                   |
| `audit_trail`  | `users`                            | Many-to-One         | Tracks which user performed the action.                |

---

## ⚙️ **Data Rules & Policies**

| **Rule**               | **Description**                                                                                        |
| ---------------------- | ------------------------------------------------------------------------------------------------------ |
| **No Deletion Policy** | All deletions use `archived = true` instead of `DELETE`.                                               |
| **30-Unit Cap**        | Enrollment transactions must not exceed 30 total units.                                                |
| **Slot Decrement**     | `sections.slots_remaining` auto-decreases when enrollment confirmed.                                   |
| **INC Policy**         | Minor → 6 months expiry, Major → 12 months expiry (auto mark repeat).                                  |
| **Audit Logging**      | Every `CREATE`, `UPDATE`, `ARCHIVE`, `RESTORE` is logged in `audit_trail`.                             |
| **Access Roles**       | Dean (Full), Registrar (Partial), Admission (Read-only), Professor (Encode only), Student (View only). |

---

## 📊 **Analytics Data Sources**

| **Metric**             | **Source Tables**               | **Computed Fields / Notes**              |
| ---------------------- | ------------------------------- | ---------------------------------------- |
| **Grade Distribution** | `grade_records`                 | Aggregated by grade per subject/section. |
| **Pass / Fail Rate**   | `enrollments`, `grade_records`  | Filter by term and status.               |
| **INC Summary**        | `inc_records`                   | Count of active vs resolved INCs.        |
| **GPA per Term**       | `grade_records`, `subjects`     | Weighted by subject units.               |
| **Faculty Load**       | `assigned_subjects`, `sections` | Count of subjects per professor.         |

---

## 🧩 **Archive Access Matrix**

| **Role**      | **Can View Archives**              | **Can Restore** | **Notes**                              |
| ------------- | ---------------------------------- | --------------- | -------------------------------------- |
| **Dean**      | ✅ Full (All Modules)              | ✅ Yes          | Full control over archive states.      |
| **Registrar** | ✅ Partial (Students, Enrollments) | ❌ No           | View-only for verification.            |
| **Admission** | ❌ None                            | ❌ No           | Read-only active data only.            |
| **Professor** | ❌ None                            | ❌ No           | Can only view active sections.         |
| **Student**   | ❌ None                            | ❌ No           | Can only view personal active records. |

---

## 🧱 **Model Groups**

| **Group**              | **Included Tables**                                                    | **Purpose**                      |
| ---------------------- | ---------------------------------------------------------------------- | -------------------------------- |
| **User & Auth**        | `users`                                                                | Authentication, RBAC             |
| **Academic Structure** | `courses`, `subjects`, `sections`, `assigned_subjects`, `school_terms` | Defines curriculum & structure   |
| **Enrollment Layer**   | `students`, `enrollments`                                              | Manages academic participation   |
| **Grades Layer**       | `grade_records`, `inc_records`                                         | Evaluation & INC policy tracking |
| **System Control**     | `audit_trail`, `archive`                                               | Traceability & compliance        |
