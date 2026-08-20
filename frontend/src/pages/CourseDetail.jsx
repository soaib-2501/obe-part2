import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/client';
import CourseSubnav from '../components/CourseSubnav';
import { useAuth } from '../context/AuthContext';

const PO_KEYS = ['PO1', 'PO2', 'PO3', 'PSO1', 'PSO2'];
const LEVELS = ['REMEMBER', 'UNDERSTAND', 'APPLY', 'ANALYZE', 'EVALUATE', 'CREATE'];

export default function CourseDetail() {
  const { id } = useParams();
  const { isAdmin } = useAuth();
  const [course, setCourse] = useState(null);
  const [facultyList, setFacultyList] = useState([]);
  const [newCO, setNewCO] = useState({ co_code: '', description: '', cognitive_level: 'UNDERSTAND' });
  const [attainments, setAttainments] = useState([]);
  const [program, setProgram] = useState([]);

  function load() {
    api.get(`/courses/${id}/`).then((res) => setCourse(res.data));
    api.get(`/attainments/?course=${id}`).then((res) => setAttainments(res.data.results ?? res.data));
    api.get(`/attainments/program/?course=${id}`).then((res) => setProgram(res.data.results ?? res.data));
  }

  useEffect(load, [id]);

  useEffect(() => {
    if (isAdmin) {
      api.get('/auth/users/?role=FACULTY').then((res) => setFacultyList(res.data.results ?? res.data));
    }
  }, [isAdmin]);

  async function addOutcome(e) {
    e.preventDefault();
    await api.post('/courses/outcomes/', {
      course: id, co_code: newCO.co_code, description: newCO.description,
      cognitive_level: newCO.cognitive_level, order: course.outcomes.length,
    });
    setNewCO({ co_code: '', description: '', cognitive_level: 'UNDERSTAND' });
    load();
  }

  async function setMapping(coId, poKey, level) {
    const co = course.outcomes.find((o) => o.id === coId);
    const existing = co.mappings.find((m) => m.po_key === poKey);
    if (existing) {
      await api.patch(`/courses/mappings/${existing.id}/`, { level: level === '' ? null : Number(level) });
    } else if (level !== '') {
      await api.post('/courses/mappings/', { course_outcome: coId, po_key: poKey, level: Number(level) });
    }
    load();
  }

  async function assignFaculty(facultyId) {
    await api.patch(`/courses/${id}/`, { faculty: facultyId === '' ? null : Number(facultyId) });
    load();
  }

  async function recalculate() {
    await api.post('/attainments/calculate/', { course: id });
    load();
  }

  if (!course) return <div className="p-8">Loading…</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link to="/courses" className="text-sm text-slate-500 hover:text-slate-700">← Back to Courses</Link>
      <h1 className="text-2xl font-bold text-slate-900 mt-2 mb-1">{course.course_code} — {course.course_name}</h1>
      <p className="text-sm text-slate-500 mb-4">{course.semester} · {course.academic_year} · NBA Code: {course.nba_code || '—'}</p>
      <CourseSubnav courseId={id} />

      <div className="bg-white shadow rounded-lg p-4 mb-6 flex flex-wrap items-center gap-3">
        <span className="text-sm text-slate-600">Assigned faculty:</span>
        {isAdmin ? (
          <select
            className="border rounded px-2 py-1.5 text-sm"
            value={course.faculty ?? ''}
            onChange={(e) => assignFaculty(e.target.value)}
          >
            <option value="">Unassigned</option>
            {facultyList.map((f) => (
              <option key={f.id} value={f.id}>{f.first_name} {f.last_name} (@{f.username})</option>
            ))}
          </select>
        ) : (
          <span className="text-sm font-medium text-slate-900">{course.faculty_name || 'Unassigned'}</span>
        )}
      </div>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-900">Course Outcomes &amp; CO-PO-PSO Mapping</h2>
          <button onClick={recalculate} className="bg-slate-900 text-white text-xs font-semibold px-3 py-1.5 rounded">
            Recalculate Attainment
          </button>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-500 border-b">
              <th className="py-2">CO</th>
              <th>Description</th>
              <th>Level</th>
              {PO_KEYS.map((p) => <th key={p} className="text-center">{p}</th>)}
              <th className="text-center">CO %</th>
            </tr>
          </thead>
          <tbody>
            {course.outcomes.map((co) => {
              const att = attainments.find((a) => a.course_outcome === co.id);
              return (
                <tr key={co.id} className="border-b last:border-0">
                  <td className="py-2 font-semibold">{co.co_code}</td>
                  <td className="pr-2 text-slate-600">{co.description}</td>
                  <td className="text-xs text-slate-500">{co.cognitive_level}</td>
                  {PO_KEYS.map((p) => {
                    const m = co.mappings.find((mm) => mm.po_key === p);
                    return (
                      <td key={p} className="text-center">
                        <select
                          className="border rounded w-14 text-center text-xs py-1"
                          value={m?.level ?? ''}
                          onChange={(e) => setMapping(co.id, p, e.target.value)}
                        >
                          <option value=""></option>
                          {[0, 1, 2, 3].map((n) => <option key={n} value={n}>{n}</option>)}
                        </select>
                      </td>
                    );
                  })}
                  <td className="text-center font-semibold">
                    {att?.final_attainment ?? '—'}
                    {att?.attainment_level != null && <span className="block text-xs text-slate-400">L{att.attainment_level}</span>}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <form onSubmit={addOutcome} className="flex gap-2 mt-4 pt-4 border-t">
          <input placeholder="CO Code (e.g. C110.2)" className="border rounded px-2 py-1.5 text-xs w-40"
            value={newCO.co_code} onChange={(e) => setNewCO({ ...newCO, co_code: e.target.value })} required />
          <input placeholder="Description" className="border rounded px-2 py-1.5 text-xs flex-1"
            value={newCO.description} onChange={(e) => setNewCO({ ...newCO, description: e.target.value })} required />
          <select className="border rounded px-2 py-1.5 text-xs" value={newCO.cognitive_level}
            onChange={(e) => setNewCO({ ...newCO, cognitive_level: e.target.value })}>
            {LEVELS.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>
          <button type="submit" className="bg-slate-200 hover:bg-slate-300 px-3 py-1.5 rounded text-xs font-semibold">
            + Add CO
          </button>
        </form>
      </div>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="font-semibold text-slate-900 mb-1">PO / PSO attainment</h2>
        <p className="text-xs text-slate-500 mb-4">
          Weighted average of CO attainment using mapping strength (1–3). Recalculate after marks and mappings are set.
        </p>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
          {PO_KEYS.map((key) => {
            const row = program.find((p) => p.po_key === key);
            return (
              <div key={key} className="border rounded p-3 text-center">
                <p className="text-xs text-slate-500">{key}</p>
                <p className="text-lg font-bold text-slate-900">{row?.percentage ?? '—'}</p>
                <p className="text-xs text-slate-400">{row?.attainment_level != null ? `Level ${row.attainment_level}` : 'No data'}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
