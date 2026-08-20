import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';

export default function Courses() {
  const [courses, setCourses] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    course_code: '', course_name: '', nba_code: '', semester: 'ODD', academic_year: '', credits: 3,
  });
  const [error, setError] = useState('');

  function load() {
    api.get('/courses/').then((res) => setCourses(res.data.results ?? res.data));
  }

  useEffect(load, []);

  async function handleCreate(e) {
    e.preventDefault();
    setError('');
    try {
      await api.post('/courses/', { ...form, outcomes: [] });
      setShowForm(false);
      setForm({ course_code: '', course_name: '', nba_code: '', semester: 'ODD', academic_year: '', credits: 3 });
      load();
    } catch (err) {
      setError(JSON.stringify(err.response?.data || 'Failed to create course'));
    }
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Courses</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded text-sm font-semibold"
        >
          {showForm ? 'Cancel' : '+ New Course'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white shadow rounded-lg p-6 mb-6 grid grid-cols-2 gap-4">
          {error && <div className="col-span-2 bg-red-50 text-red-700 text-xs rounded p-2">{error}</div>}
          <input placeholder="Course Code (e.g. 17M11CS111)" className="border rounded px-3 py-2 text-sm"
            value={form.course_code} onChange={(e) => setForm({ ...form, course_code: e.target.value })} required />
          <input placeholder="NBA Code (e.g. C110)" className="border rounded px-3 py-2 text-sm"
            value={form.nba_code} onChange={(e) => setForm({ ...form, nba_code: e.target.value })} />
          <input placeholder="Course Name" className="border rounded px-3 py-2 text-sm col-span-2"
            value={form.course_name} onChange={(e) => setForm({ ...form, course_name: e.target.value })} required />
          <select className="border rounded px-3 py-2 text-sm" value={form.semester}
            onChange={(e) => setForm({ ...form, semester: e.target.value })}>
            <option value="ODD">Odd</option>
            <option value="EVEN">Even</option>
          </select>
          <input placeholder="Academic Year (e.g. 2025-26)" className="border rounded px-3 py-2 text-sm"
            value={form.academic_year} onChange={(e) => setForm({ ...form, academic_year: e.target.value })} required />
          <input type="number" placeholder="Credits" className="border rounded px-3 py-2 text-sm"
            value={form.credits} onChange={(e) => setForm({ ...form, credits: Number(e.target.value) })} />
          <button type="submit" className="col-span-2 bg-slate-900 text-white py-2 rounded text-sm font-semibold">
            Create Course
          </button>
        </form>
      )}

      <div className="bg-white shadow rounded-lg divide-y">
        {courses.length === 0 && <p className="p-6 text-sm text-slate-400">No courses yet — create one above.</p>}
        {courses.map((c) => (
          <Link key={c.id} to={`/courses/${c.id}`} className="flex items-center justify-between p-4 hover:bg-slate-50">
            <div>
              <p className="font-semibold text-slate-900">{c.course_code} — {c.course_name}</p>
              <p className="text-xs text-slate-500">{c.semester} · {c.academic_year} · {c.credits} credits</p>
            </div>
            <span className="text-xs text-slate-400">{c.outcomes?.length ?? 0} COs →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
