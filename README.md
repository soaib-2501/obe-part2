# OBE Management System — Part 2

Web platform for **Outcome-Based Education** course offerings: Course Description, Opening Report, assessments, CO/PO/PSO attainment, and projects.

```
React (Vite + Tailwind)  →  Django REST + JWT  →  PostgreSQL (Neon)
```

## Roles

| Role | Access |
|------|--------|
| **ADMIN** | All courses, user management (create faculty/admin accounts) |
| **FACULTY** | Only their own course offerings |

A course offering is unique per **`(course_code, academic_year, faculty)`**. The same subject in a new session is a new Course row.

## What the app does

### Course Description
Faculty enter and save syllabus data, then preview / print / save as PDF:

- Header (title, institute), basic info (code, name, program, department, semester, session, NBA code)
- Coordinator names, course outcomes (COs) and cognitive levels
- Lecture-wise breakup, evaluation criteria, PBL, textbooks / reference books
- CO–PO–PSO mapping (level 0–3 + justification). PO/PSO counts are editable (e.g. B.Tech vs M.Tech)

COs and mapping live on the Course. Other documents **read** this data; they do not duplicate it.

### Opening Report
Synced from Course Description (header, COs, mapping). Faculty fill report-only fields:

- Gaps / modifications in syllabus (or NIL)
- Previous-year CO attainment (loaded from historical records, not invented)
- **Target attainment** per CO (faculty-set; optional suggested average from loaded years)
- Actions to improve CO attainment; Strengthens POs/PSOs from mapping (`level > 0`)
- Teaching methods, weak/bright strategies, evaluation strategy, appendix (guidelines, efforts, impact)

Preview and **Print / Save as PDF** use the same document layout as Course Description.

Historical attainment is keyed by **`course_code + academic_year + semester + co_code`**, not the current Course PK, so last year’s offering still applies.

### Attainment
Recalculate from student marks:

- Direct = 60% tests (T1/T2/T3) + 20% assignment  
- Indirect = 20% course-exit feedback  
- Final = direct + indirect; level 0–3 from percentage  
- PO/PSO attainment from CO attainment × mapping strength  

### Also included
- Students & marks entry per assessment type  
- Assessment report (class averages by assessment and by CO)  
- Projects  
- Dashboard  
- Admin user management  

## Folder structure

```
obe-part2/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── obe_backend/              # settings, URLs, dashboard
│   ├── users/                    # JWT auth, ADMIN | FACULTY
│   ├── courses/                  # Course, COs, mapping, modules, books
│   ├── assessments/              # Assessment, Student, StudentMark
│   ├── attainments/              # CO/PO calculation + HistoricalCoAttainment
│   ├── opening_reports/          # OpeningReport (OneToOne Course)
│   └── projects/
├── frontend/
│   └── src/
│       ├── api/client.js         # axios + JWT refresh
│       ├── context/AuthContext.jsx
│       ├── components/           # Navbar, CourseSubnav, ProtectedRoute
│       └── pages/                # Login, Courses, Course Description,
│                                 # Opening Report, Assessments, Reports, …
└── README.md
```

## API (prefix `/api`)

| Area | Path |
|------|------|
| Auth / users | `/auth/` |
| Dashboard | `/dashboard/` |
| Courses, COs, mappings | `/courses/` |
| Opening report | `/opening-reports/<course_id>/` |
| Assessments, students, marks | `/assessments/` |
| CO/PO attainment + calculate | `/attainments/` |
| Historical CO attainment | `/attainments/historical/?course=&academic_year=` |
| Projects | `/projects/` |

## First-time setup

### 1. Database
Use **PostgreSQL** (Neon is configured via `DATABASE_URL`). Prefer a database separate from any Part 1 project.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate              # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env             # set DATABASE_URL, SECRET_KEY
python manage.py migrate
python manage.py createsuperuser   # first Admin
python manage.py runserver         # http://localhost:8000
```

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env             # default: http://localhost:8000/api
npm run dev                        # http://localhost:5173
```

Sign in at `http://localhost:5173`. Faculty accounts are created by an Admin on **Users**.

## Typical course workflow

1. Create a course for this **session** (code + academic year + faculty).  
2. **Course Description** — fill COs, mapping, syllabus; Save; Print if needed.  
3. **Opening Report** — confirm synced CD data; set targets; Save; Print.  
4. **Students & Marks** — enter assessments.  
5. **Attainment** — recalculate; check PO/PSO.  
6. **Assessment Report** — print class summary.

Print / Save as PDF uses the browser print dialog (A4). Choose “Save as PDF” as the destination.

## Environment

**Backend `.env`** (see `backend/.env.example`):

- `SECRET_KEY`, `DEBUG`  
- `DATABASE_URL` — Neon Postgres  
- `CORS_ALLOWED_ORIGINS` — e.g. `http://localhost:5173`  

**Frontend `.env`:** `VITE_API_BASE_URL=http://localhost:8000/api`
