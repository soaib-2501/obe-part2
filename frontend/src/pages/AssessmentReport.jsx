import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import CourseSubnav from '../components/CourseSubnav';

const TYPE_LABELS = {
  T1: 'Test 1',
  T2: 'Test 2',
  T3: 'Test 3',
  ASSIGNMENT: 'Assignment',
  ATTENDANCE: 'Attendance',
  PROJECT: 'Project',
  FEEDBACK: 'Course Exit Feedback',
};

export default function AssessmentReport() {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [report, setReport] = useState(null);
  const [program, setProgram] = useState([]);

  useEffect(() => {
    api.get(`/courses/${id}/`).then((res) => setCourse(res.data));
    api.get(`/assessments/report/?course=${id}`).then((res) => setReport(res.data));
    api.get(`/attainments/program/?course=${id}`).then((res) => setProgram(res.data.results ?? res.data));
  }, [id]);

  if (!course || !report) return <div className="p-8">Loading…</div>;

  return (
    <div className="p-8 max-w-5xl mx-auto print:p-0">
      <div className="print:hidden">
        <Link to="/courses" className="text-sm text-slate-500 hover:text-slate-700">← Back to Courses</Link>
        <h1 className="text-2xl font-bold text-slate-900 mt-2 mb-1">{course.course_code} — {course.course_name}</h1>
        <p className="text-sm text-slate-500 mb-4">{course.semester} · {course.academic_year}</p>
        <CourseSubnav courseId={id} />
        <div className="flex justify-end mb-4">
          <button type="button" onClick={() => window.print()} className="bg-slate-900 text-white text-sm font-semibold px-4 py-2 rounded">
            Print / Save as PDF
          </button>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6 print:shadow-none">
        <h2 className="text-xl font-bold text-slate-900">Assessment Report</h2>
        <p className="text-sm text-slate-500 mt-1">
          {course.course_code} · {report.student_count} students · Faculty: {course.faculty_name || 'Unassigned'}
        </p>

        <table className="w-full text-sm mt-6">
          <thead>
            <tr className="text-left text-slate-500 border-b">
              <th className="py-2">Assessment</th>
              <th>Max</th>
              <th>Class average</th>
              <th>Entries</th>
              <th>By CO</th>
            </tr>
          </thead>
          <tbody>
            {report.assessments.length === 0 && (
              <tr><td colSpan="5" className="py-4 text-slate-400">No assessments yet.</td></tr>
            )}
            {report.assessments.map((a) => (
              <tr key={a.id} className="border-b last:border-0 align-top">
                <td className="py-2 font-medium">{TYPE_LABELS[a.assessment_type] || a.assessment_type}</td>
                <td>{a.max_marks}</td>
                <td>{a.class_average ?? '—'}</td>
                <td>{a.entry_count}</td>
                <td className="text-xs text-slate-600">
                  {a.by_co.map((c) => `${c.co_code}: ${c.average}`).join(' · ') || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <h3 className="font-semibold text-slate-900 mt-8 mb-3">PO / PSO attainment</h3>
        <div className="grid grid-cols-5 gap-3">
          {['PO1', 'PO2', 'PO3', 'PSO1', 'PSO2'].map((key) => {
            const row = program.find((p) => p.po_key === key);
            return (
              <div key={key} className="border rounded p-3 text-center">
                <p className="text-xs text-slate-500">{key}</p>
                <p className="font-bold">{row?.percentage ?? '—'}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
