# OBE Management System — Part 2 (Full SRS System)

This is **Part 2**: the complete platform built strictly to `SOFTWARE_REQUIREMENTS_SPECIFICATION.docx`
(v1.0) — separate from Part 1 (the standalone document generators). Architecture, per the SRS:

```
Frontend (React) → REST API (Django) → Business Logic Layer → PostgreSQL Database → Document Generation Engine
```

`Document Generation Engine` in that diagram is Part 1 — the two connect later (see the "Connecting to
Part 1" section at the bottom).

## Folder structure

```
obe-full-system/
├── backend/                         # Django + Django REST Framework
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── obe_backend/                 # project settings/urls
│   │   ├── settings.py
│   │   └── urls.py
│   ├── users/                       # Auth + role-based access (SRS 3.1, 2.3 User Mgmt)
│   │   ├── models.py                # custom User model — role: ADMIN | FACULTY
│   │   ├── views.py                 # JWT login, /me/, admin-only user CRUD
│   │   └── permissions.py           # IsAdminRole, IsFacultyRole
│   ├── courses/                     # SRS 3.2, 3.3, 3.4
│   │   └── models.py                # Course, CourseOutcome, CoPoMapping
│   ├── assessments/                 # SRS 3.5
│   │   └── models.py                # Assessment, Student, StudentMark
│   ├── attainments/                 # SRS 3.6
│   │   ├── models.py                # Attainment (per Course Outcome)
│   │   └── services.py              # the actual CO/PO/PSO calculation engine
│   └── projects/                    # SRS 3.7
│       └── models.py                # Project
│
├── frontend/                        # React (Vite) + Tailwind
│   └── src/
│       ├── api/client.js            # axios instance + JWT auto-refresh
│       ├── context/AuthContext.jsx  # login/logout/current user
│       ├── components/              # Navbar, ProtectedRoute
│       └── pages/                   # Login, Dashboard, Courses, CourseDetail
│
└── README.md                        # this file
```

## Why one Django app per SRS module

Each SRS functional-requirement section (3.1–3.7) became its own Django app. This mirrors the SRS
directly — when you present, "Section 3.4 CO-PO-PSO Mapping" maps to literally `courses/models.py`'s
`CoPoMapping` model, nothing is scattered. It also means finishing one module (e.g. `projects/`) doesn't
risk breaking another.

## What's implemented vs. stubbed

**Backend — fully working:**
- JWT authentication with `role` (Admin/Faculty) embedded in the token
- Full CRUD for Courses, Course Outcomes, CO-PO-PSO Mapping, Assessments, Students, Marks, Projects
- The attainment calculation engine (`attainments/services.py`) — reads `StudentMark` rows and computes
  Direct (60% test + 20% assignment), Indirect (20% feedback), Final attainment, and a 0–3 attainment level,
  the same formula used in Part 1's Closing Report template
- Role-based permissions — only Admins can add/remove faculty accounts

**Frontend — core flow working, rest stubbed intentionally:**
- Login → Dashboard → Course list → Create course → Course detail (add COs, edit the CO-PO-PSO mapping
  grid inline, trigger attainment recalculation) all work end-to-end against the real API
- Assessment/marks entry UI, the Projects page, and Dashboard analytics are **not built yet** — the
  backend APIs for them already exist (`/api/assessments/`, `/api/projects/`), only the frontend pages
  are pending. This was a deliberate scope cut to have one clean vertical slice working end-to-end
  rather than many half-built pages.

## First-time setup

### 1. Neon database
Create a **separate database** for Part 2 (keep it isolated from Part 1's data) — either a new database
inside your existing Neon project, or a new Neon project entirely. Copy its connection string.

### 2. Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # paste your Neon connection string into DATABASE_URL
python manage.py migrate          # migrations are already written — this just applies them
python manage.py createsuperuser  # make your first Admin account
python manage.py runserver        # http://localhost:8000
```

### 3. Frontend
```bash
cd frontend
npm install
cp .env.example .env              # defaults to http://localhost:8000/api, fine for local dev
npm run dev                       # http://localhost:5173
```

Open `http://localhost:5173`, log in with the superuser you created, and you're in.

## Connecting to Part 1 (future step)

Right now Part 1's HTML generators and Part 2's Django system are independent. The planned integration:
Part 2 becomes the source of truth (courses, COs, marks, attainment all live in its Postgres database);
when a document needs to be generated, Part 2's backend will call Part 1's generator (or Part 1's own
save/load API from the Neon-backed Course Description you already built) with the current data, instead
of a user re-entering it by hand. That's the `Document Generation Engine` box in the SRS architecture
diagram — Part 1 fills that role.
