import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import CourseSubnav from '../components/CourseSubnav';

const STATUSES = [
  { value: 'NOT_STARTED', label: 'Not Started' },
  { value: 'IN_PROGRESS', label: 'In Progress' },
  { value: 'EVALUATED', label: 'Evaluated' },
];

const STATUS_STYLES = {
  NOT_STARTED: 'bg-slate-100 text-slate-700',
  IN_PROGRESS: 'bg-amber-100 text-amber-800',
  EVALUATED: 'bg-emerald-100 text-emerald-800',
};

function list(data) {
  return data?.results ?? data ?? [];
}

const emptyForm = {
  course: '',
  project_title: '',
  student_names: '',
  evaluation_status: 'NOT_STARTED',
  marks_obtained: '',
  remarks: '',
};

export default function Projects() {
  const { id: courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [courses, setCourses] = useState([]);
  const [projects, setProjects] = useState([]);
  const [filter, setFilter] = useState('');
  const [form, setForm] = useState({ ...emptyForm, course: courseId ?? '' });
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');

  async function load() {
    setError('');
    const params = [];
    if (courseId) params.push(`course=${courseId}`);
    if (filter) params.push(`status=${filter}`);
    const qs = params.length ? `?${params.join('&')}` : '';

    const requests = [api.get(`/projects/${qs}`)];
    if (courseId) {
      requests.push(api.get(`/courses/${courseId}/`));
    } else {
      requests.push(api.get('/courses/'));
    }
    const [projectRes, courseRes] = await Promise.all(requests);
    setProjects(list(projectRes.data));
    if (courseId) {
      setCourse(courseRes.data);
    } else {
      setCourses(list(courseRes.data));
    }
  }

  useEffect(() => {
    setForm({ ...emptyForm, course: courseId ?? '' });
    setEditingId(null);
    setShowForm(false);
    load().catch(() => setError('Failed to load projects.'));
  }, [courseId, filter]);

  function startEdit(project) {
    setEditingId(project.id);
    setShowForm(true);
    setForm({
      course: String(project.course),
      project_title: project.project_title,
      student_names: project.student_names,
      evaluation_status: project.evaluation_status,
      marks_obtained: project.marks_obtained ?? '',
      remarks: project.remarks ?? '',
    });
  }

  function resetForm() {
    setEditingId(null);
    setShowForm(false);
    setForm({ ...emptyForm, course: courseId ?? '' });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    const payload = {
      course: Number(form.course),
      project_title: form.project_title,
      student_names: form.student_names,
      evaluation_status: form.evaluation_status,
      marks_obtained: form.marks_obtained === '' ? null : Number(form.marks_obtained),
      remarks: form.remarks,
    };
    try {
      if (editingId) {
        await api.patch(`/projects/${editingId}/`, payload);
      } else {
        await api.post('/projects/', payload);
      }
      resetForm();
      await load();
    } catch (err) {
      const data = err.response?.data;
      setError(typeof data === 'string' ? data : JSON.stringify(data || 'Could not save project.'));
    }
  }

  async function updateStatus(project, evaluation_status) {
    await api.patch(`/projects/${project.id}/`, { evaluation_status });
    await load();
  }

  async function deleteProject(projectId) {
    if (!window.confirm('Delete this project?')) return;
    await api.delete(`/projects/${projectId}/`);
    await load();
  }

  const heading = course
    ? `${course.course_code} — ${course.course_name}`
    : 'Projects';

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {courseId ? (
        <>
          <Link to="/courses" className="text-sm text-slate-500 hover:text-slate-700">← Back to Courses</Link>
          <h1 className="text-2xl font-bold text-slate-900 mt-2 mb-1">{heading}</h1>
          <p className="text-sm text-slate-500 mb-4">{course?.semester} · {course?.academic_year}</p>
          <CourseSubnav courseId={courseId} />
        </>
      ) : (
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Projects</h1>
            <p className="text-sm text-slate-500 mt-1">Track group projects and evaluation status across courses.</p>
          </div>
        </div>
      )}

      {error && <div className="bg-red-50 text-red-700 text-sm rounded p-3 mb-4">{error}</div>}

      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <select
          className="border rounded px-3 py-1.5 text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">All statuses</option>
          {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <button
          type="button"
          onClick={() => { setShowForm((v) => !v); if (showForm) resetForm(); }}
          className="bg-slate-900 text-white px-4 py-2 rounded text-sm font-semibold"
        >
          {showForm ? 'Cancel' : editingId ? 'Cancel edit' : '+ New Project'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6 mb-6 grid grid-cols-2 gap-4">
          {!courseId && (
            <select
              className="border rounded px-3 py-2 text-sm col-span-2"
              value={form.course}
              onChange={(e) => setForm({ ...form, course: e.target.value })}
              required
            >
              <option value="">Select course</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>{c.course_code} — {c.course_name}</option>
              ))}
            </select>
          )}
          <input
            placeholder="Project title"
            className="border rounded px-3 py-2 text-sm col-span-2"
            value={form.project_title}
            onChange={(e) => setForm({ ...form, project_title: e.target.value })}
            required
          />
          <input
            placeholder="Group members (comma-separated)"
            className="border rounded px-3 py-2 text-sm col-span-2"
            value={form.student_names}
            onChange={(e) => setForm({ ...form, student_names: e.target.value })}
            required
          />
          <select
            className="border rounded px-3 py-2 text-sm"
            value={form.evaluation_status}
            onChange={(e) => setForm({ ...form, evaluation_status: e.target.value })}
          >
            {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
          <input
            type="number"
            min="0"
            step="0.5"
            placeholder="Marks (optional)"
            className="border rounded px-3 py-2 text-sm"
            value={form.marks_obtained}
            onChange={(e) => setForm({ ...form, marks_obtained: e.target.value })}
          />
          <textarea
            placeholder="Remarks"
            className="border rounded px-3 py-2 text-sm col-span-2 h-20"
            value={form.remarks}
            onChange={(e) => setForm({ ...form, remarks: e.target.value })}
          />
          <button type="submit" className="col-span-2 bg-slate-900 text-white py-2 rounded text-sm font-semibold">
            {editingId ? 'Update Project' : 'Create Project'}
          </button>
        </form>
      )}

      <div className="bg-white shadow rounded-lg overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b">
              <th className="p-3">Project</th>
              {!courseId && <th className="p-3">Course</th>}
              <th className="p-3">Group</th>
              <th className="p-3">Status</th>
              <th className="p-3">Marks</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {projects.length === 0 && (
              <tr>
                <td colSpan={courseId ? 5 : 6} className="p-6 text-slate-400">No projects yet.</td>
              </tr>
            )}
            {projects.map((p) => (
              <tr key={p.id} className="border-b last:border-0 align-top">
                <td className="p-3">
                  <p className="font-semibold text-slate-900">{p.project_title}</p>
                  {p.remarks && <p className="text-xs text-slate-500 mt-1">{p.remarks}</p>}
                </td>
                {!courseId && (
                  <td className="p-3">
                    <Link to={`/courses/${p.course}/projects`} className="text-slate-700 hover:underline">
                      {p.course_code}
                    </Link>
                  </td>
                )}
                <td className="p-3 text-slate-600">{p.student_names}</td>
                <td className="p-3">
                  <select
                    className={`border rounded px-2 py-1 text-xs font-medium ${STATUS_STYLES[p.evaluation_status]}`}
                    value={p.evaluation_status}
                    onChange={(e) => updateStatus(p, e.target.value)}
                  >
                    {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </td>
                <td className="p-3">{p.marks_obtained ?? '—'}</td>
                <td className="p-3 text-right whitespace-nowrap">
                  <button type="button" onClick={() => startEdit(p)} className="text-xs text-slate-600 hover:underline mr-3">
                    Edit
                  </button>
                  <button type="button" onClick={() => deleteProject(p.id)} className="text-xs text-red-600 hover:underline">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
