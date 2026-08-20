import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import CourseSubnav from '../components/CourseSubnav';

const ASSESSMENT_TYPES = [
  { value: 'T1', label: 'Test 1' },
  { value: 'T2', label: 'Test 2' },
  { value: 'T3', label: 'Test 3' },
  { value: 'ASSIGNMENT', label: 'Assignment' },
  { value: 'ATTENDANCE', label: 'Attendance' },
  { value: 'PROJECT', label: 'Project' },
  { value: 'FEEDBACK', label: 'Course Exit Feedback' },
];

const DEFAULT_MAX = {
  T1: 30,
  T2: 30,
  T3: 30,
  ASSIGNMENT: 20,
  ATTENDANCE: 5,
  PROJECT: 20,
  FEEDBACK: 5,
};

function typeLabel(value) {
  return ASSESSMENT_TYPES.find((t) => t.value === value)?.label ?? value;
}

function list(data) {
  return data?.results ?? data ?? [];
}

export default function CourseAssessments() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [students, setStudents] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [marks, setMarks] = useState([]);
  const [grid, setGrid] = useState({});
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [saving, setSaving] = useState(false);

  const [studentForm, setStudentForm] = useState({ roll_number: '', name: '' });
  const [bulkText, setBulkText] = useState('');
  const [showBulk, setShowBulk] = useState(false);

  const [newType, setNewType] = useState('T1');
  const [newMax, setNewMax] = useState(DEFAULT_MAX.T1);

  const outcomes = course?.outcomes ?? [];
  const selected = assessments.find((a) => a.id === selectedId) ?? null;

  async function loadCourseAndLists() {
    const [courseRes, studentRes, assessmentRes] = await Promise.all([
      api.get(`/courses/${id}/`),
      api.get(`/assessments/students/?course=${id}`),
      api.get(`/assessments/?course=${id}`),
    ]);
    setCourse(courseRes.data);
    setStudents(list(studentRes.data));
    const nextAssessments = list(assessmentRes.data);
    setAssessments(nextAssessments);
    setSelectedId((prev) => {
      if (prev && nextAssessments.some((a) => a.id === prev)) return prev;
      return nextAssessments[0]?.id ?? null;
    });
  }

  async function loadMarks(assessmentId) {
    if (!assessmentId) {
      setMarks([]);
      setGrid({});
      return;
    }
    const res = await api.get(`/assessments/marks/?assessment=${assessmentId}`);
    const rows = list(res.data);
    setMarks(rows);
    const next = {};
    rows.forEach((row) => {
      next[`${row.student}-${row.course_outcome}`] = String(row.marks_obtained);
    });
    setGrid(next);
  }

  useEffect(() => {
    loadCourseAndLists().catch(() => setError('Failed to load course data.'));
  }, [id]);

  useEffect(() => {
    loadMarks(selectedId).catch(() => setError('Failed to load marks.'));
  }, [selectedId]);

  const usedTypes = useMemo(() => new Set(assessments.map((a) => a.assessment_type)), [assessments]);
  const availableTypes = ASSESSMENT_TYPES.filter((t) => !usedTypes.has(t.value));

  useEffect(() => {
    if (!availableTypes.some((t) => t.value === newType)) {
      const next = availableTypes[0];
      setNewType(next?.value ?? '');
      setNewMax(next ? DEFAULT_MAX[next.value] : 10);
    }
  }, [availableTypes, newType]);

  function cellKey(studentId, coId) {
    return `${studentId}-${coId}`;
  }

  function setCell(studentId, coId, value) {
    setGrid((prev) => ({ ...prev, [cellKey(studentId, coId)]: value }));
  }

  async function addStudent(e) {
    e.preventDefault();
    setError('');
    try {
      await api.post('/assessments/students/', { ...studentForm, course: Number(id) });
      setStudentForm({ roll_number: '', name: '' });
      await loadCourseAndLists();
    } catch (err) {
      setError(formatError(err, 'Could not add student.'));
    }
  }

  async function addBulkStudents(e) {
    e.preventDefault();
    setError('');
    const lines = bulkText.split('\n').map((line) => line.trim()).filter(Boolean);
    const payload = [];
    for (const line of lines) {
      const [roll_number, ...rest] = line.split(/[,\t]/).map((part) => part.trim());
      const name = rest.join(' ').trim();
      if (!roll_number || !name) {
        setError('Each line must be: roll number, name');
        return;
      }
      payload.push({ roll_number, name, course: Number(id) });
    }
    try {
      for (const row of payload) {
        await api.post('/assessments/students/', row);
      }
      setBulkText('');
      setShowBulk(false);
      await loadCourseAndLists();
    } catch (err) {
      setError(formatError(err, 'Could not import students.'));
    }
  }

  async function deleteStudent(studentId) {
    if (!window.confirm('Remove this student and their marks from the course?')) return;
    setError('');
    await api.delete(`/assessments/students/${studentId}/`);
    await loadCourseAndLists();
    await loadMarks(selectedId);
  }

  async function addAssessment(e) {
    e.preventDefault();
    setError('');
    if (!newType) return;
    try {
      const res = await api.post('/assessments/', {
        course: Number(id),
        assessment_type: newType,
        max_marks: Number(newMax),
      });
      await loadCourseAndLists();
      setSelectedId(res.data.id);
      const remaining = ASSESSMENT_TYPES.filter(
        (t) => t.value !== newType && !usedTypes.has(t.value)
      );
      const nextType = remaining[0]?.value ?? '';
      setNewType(nextType);
      setNewMax(nextType ? DEFAULT_MAX[nextType] : 10);
    } catch (err) {
      setError(formatError(err, 'Could not create assessment.'));
    }
  }

  async function deleteAssessment(assessmentId) {
    if (!window.confirm('Delete this assessment and all of its marks?')) return;
    setError('');
    await api.delete(`/assessments/${assessmentId}/`);
    await loadCourseAndLists();
  }

  async function saveMarks({ recalculate }) {
    if (!selected) return;
    setError('');
    setStatus('');
    setSaving(true);
    try {
      const toUpsert = [];
      const toDelete = [];
      for (const student of students) {
        for (const co of outcomes) {
          const key = cellKey(student.id, co.id);
          const raw = grid[key];
          const existing = marks.find(
            (m) => m.student === student.id && m.course_outcome === co.id
          );
          if (raw === undefined || raw === '') {
            if (existing) toDelete.push(existing.id);
            continue;
          }
          const marksObtained = Number(raw);
          if (Number.isNaN(marksObtained)) {
            setError(`Invalid mark for ${student.roll_number} / ${co.co_code}.`);
            setSaving(false);
            return;
          }
          if (marksObtained < 0 || marksObtained > selected.max_marks) {
            setError(`Marks for ${student.roll_number} must be between 0 and ${selected.max_marks}.`);
            setSaving(false);
            return;
          }
          toUpsert.push({
            assessment: selected.id,
            student: student.id,
            course_outcome: co.id,
            marks_obtained: marksObtained,
          });
        }
      }
      if (toUpsert.length) {
        await api.post('/assessments/marks/', toUpsert);
      }
      await Promise.all(toDelete.map((markId) => api.delete(`/assessments/marks/${markId}/`)));
      if (recalculate) {
        await api.post('/attainments/calculate/', { course: Number(id) });
        setStatus('Marks saved and attainment recalculated.');
      } else {
        setStatus('Marks saved.');
      }
      await loadMarks(selected.id);
    } catch (err) {
      setError(formatError(err, 'Could not save marks.'));
    } finally {
      setSaving(false);
    }
  }

  if (!course) return <div className="p-8">Loading…</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <Link to="/courses" className="text-sm text-slate-500 hover:text-slate-700">← Back to Courses</Link>
      <h1 className="text-2xl font-bold text-slate-900 mt-2 mb-1">{course.course_code} — {course.course_name}</h1>
      <p className="text-sm text-slate-500 mb-4">{course.semester} · {course.academic_year}</p>
      <CourseSubnav courseId={id} />

      {error && <div className="bg-red-50 text-red-700 text-sm rounded p-3 mb-4">{error}</div>}
      {status && <div className="bg-emerald-50 text-emerald-800 text-sm rounded p-3 mb-4">{status}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <section className="lg:col-span-2 bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Students</h2>
            <button
              type="button"
              onClick={() => setShowBulk((v) => !v)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900"
            >
              {showBulk ? 'Hide bulk import' : 'Bulk import'}
            </button>
          </div>

          <form onSubmit={addStudent} className="flex gap-2 mb-3">
            <input
              placeholder="Roll number"
              className="border rounded px-2 py-1.5 text-sm w-40"
              value={studentForm.roll_number}
              onChange={(e) => setStudentForm({ ...studentForm, roll_number: e.target.value })}
              required
            />
            <input
              placeholder="Name"
              className="border rounded px-2 py-1.5 text-sm flex-1"
              value={studentForm.name}
              onChange={(e) => setStudentForm({ ...studentForm, name: e.target.value })}
              required
            />
            <button type="submit" className="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-semibold">
              Add
            </button>
          </form>

          {showBulk && (
            <form onSubmit={addBulkStudents} className="mb-4">
              <textarea
                className="w-full border rounded px-3 py-2 text-sm h-28"
                placeholder={'One student per line: roll number, name\n1RN21CS001, Aisha Khan'}
                value={bulkText}
                onChange={(e) => setBulkText(e.target.value)}
              />
              <button type="submit" className="mt-2 bg-slate-200 hover:bg-slate-300 px-3 py-1.5 rounded text-xs font-semibold">
                Import students
              </button>
            </form>
          )}

          <div className="border rounded divide-y max-h-56 overflow-auto">
            {students.length === 0 && <p className="p-3 text-sm text-slate-400">No students yet.</p>}
            {students.map((s) => (
              <div key={s.id} className="flex items-center justify-between px-3 py-2 text-sm">
                <div>
                  <span className="font-medium text-slate-900">{s.roll_number}</span>
                  <span className="text-slate-500"> · {s.name}</span>
                </div>
                <button type="button" onClick={() => deleteStudent(s.id)} className="text-xs text-red-600 hover:underline">
                  Remove
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white shadow rounded-lg p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Assessments</h2>
          <form onSubmit={addAssessment} className="space-y-2 mb-4">
            <select
              className="w-full border rounded px-2 py-1.5 text-sm"
              value={newType}
              onChange={(e) => {
                setNewType(e.target.value);
                setNewMax(DEFAULT_MAX[e.target.value] ?? 10);
              }}
              disabled={!availableTypes.length}
            >
              {availableTypes.length === 0 && <option value="">All types added</option>}
              {availableTypes.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <input
              type="number"
              min="1"
              className="w-full border rounded px-2 py-1.5 text-sm"
              value={newMax}
              onChange={(e) => setNewMax(e.target.value)}
              disabled={!availableTypes.length}
            />
            <button
              type="submit"
              disabled={!availableTypes.length}
              className="w-full bg-slate-900 text-white py-1.5 rounded text-sm font-semibold disabled:opacity-50"
            >
              Add assessment
            </button>
          </form>

          <div className="space-y-1">
            {assessments.length === 0 && <p className="text-sm text-slate-400">No assessments yet.</p>}
            {assessments.map((a) => (
              <div
                key={a.id}
                className={`flex items-center justify-between rounded px-3 py-2 text-sm cursor-pointer ${
                  a.id === selectedId ? 'bg-slate-900 text-white' : 'hover:bg-slate-50'
                }`}
                onClick={() => setSelectedId(a.id)}
              >
                <span>{typeLabel(a.assessment_type)} · max {a.max_marks}</span>
                <button
                  type="button"
                  className={`text-xs ${a.id === selectedId ? 'text-slate-300' : 'text-red-600'} hover:underline`}
                  onClick={(e) => { e.stopPropagation(); deleteAssessment(a.id); }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="bg-white shadow rounded-lg p-6">
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div>
            <h2 className="font-semibold text-slate-900">Marks entry</h2>
            <p className="text-xs text-slate-500 mt-1">
              {selected
                ? `${typeLabel(selected.assessment_type)} — enter marks out of ${selected.max_marks} for each CO. Empty cells are not saved.`
                : 'Create an assessment to enter marks.'}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={!selected || saving || !students.length || !outcomes.length}
              onClick={() => saveMarks({ recalculate: false })}
              className="bg-slate-200 hover:bg-slate-300 px-3 py-1.5 rounded text-sm font-semibold disabled:opacity-50"
            >
              {saving ? 'Saving…' : 'Save marks'}
            </button>
            <button
              type="button"
              disabled={!selected || saving || !students.length || !outcomes.length}
              onClick={() => saveMarks({ recalculate: true })}
              className="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-semibold disabled:opacity-50"
            >
              Save & recalculate
            </button>
          </div>
        </div>

        {!outcomes.length && (
          <p className="text-sm text-slate-500">Add course outcomes on the mapping tab before entering marks.</p>
        )}
        {outcomes.length > 0 && students.length === 0 && (
          <p className="text-sm text-slate-500">Add students above before entering marks.</p>
        )}

        {selected && students.length > 0 && outcomes.length > 0 && (
          <div className="overflow-auto">
            <table className="w-full text-sm min-w-[640px]">
              <thead>
                <tr className="text-left text-slate-500 border-b">
                  <th className="py-2 pr-3">Roll</th>
                  <th className="pr-3">Name</th>
                  {outcomes.map((co) => (
                    <th key={co.id} className="text-center px-1">{co.co_code}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b last:border-0">
                    <td className="py-2 pr-3 font-medium whitespace-nowrap">{s.roll_number}</td>
                    <td className="pr-3 text-slate-600 whitespace-nowrap">{s.name}</td>
                    {outcomes.map((co) => (
                      <td key={co.id} className="text-center px-1 py-1">
                        <input
                          type="number"
                          min="0"
                          max={selected.max_marks}
                          step="0.5"
                          className="border rounded w-16 text-center text-xs py-1"
                          value={grid[cellKey(s.id, co.id)] ?? ''}
                          onChange={(e) => setCell(s.id, co.id, e.target.value)}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function formatError(err, fallback) {
  const data = err.response?.data;
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  try {
    return JSON.stringify(data);
  } catch {
    return fallback;
  }
}
