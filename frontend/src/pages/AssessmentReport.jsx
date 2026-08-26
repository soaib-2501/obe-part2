import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client';
import CourseSubnav from '../components/CourseSubnav';
import A4Document from '../components/A4Document';
import { a4TableBlocks } from '../components/a4TableBlocks';

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

  const previewRevision = JSON.stringify({ course, report, program });
  const poKeys = course.po_pso_keys || [];

  return (
    <div className="print:p-0">
      <div className="no-print p-8 max-w-5xl mx-auto">
        <Link to="/courses" className="text-sm text-slate-500 hover:text-slate-700">← Back to Courses</Link>
        <h1 className="text-2xl font-bold text-slate-900 mt-2 mb-1">{course.course_code} — {course.course_name}</h1>
        <p className="text-sm text-slate-500 mb-4">
          {course.program_name ? `${course.program_name} · ` : ''}{course.semester} · {course.academic_year}
        </p>
        <CourseSubnav courseId={id} />
        <div className="flex justify-end mb-4">
          <button type="button" onClick={() => window.print()} className="bg-slate-900 text-white text-sm font-semibold px-4 py-2 rounded">
            Print / Save as PDF
          </button>
        </div>
      </div>

      <A4Document revision={previewRevision}>
        <div>
          <div className="border-b border-slate-800 pb-3 mb-4 text-center">
            <p className="text-xl font-bold text-slate-900 uppercase tracking-wide">Assessment Report</p>
            <p className="text-[11px] mt-1 break-words">
              {course.course_code} · {course.course_name}
            </p>
            <p className="text-[11px] mt-0.5">
              {report.student_count} students · Faculty: {course.faculty_name || 'Unassigned'}
            </p>
          </div>
        </div>

        {a4TableBlocks({
          title: 'Assessments',
          head: (
            <tr>
              <th className="bg-slate-50 w-[22%]">Assessment</th>
              <th className="bg-slate-50 w-[12%]">Max</th>
              <th className="bg-slate-50 w-[16%]">Class average</th>
              <th className="bg-slate-50 w-[12%]">Entries</th>
              <th className="bg-slate-50">By CO</th>
            </tr>
          ),
          rows: report.assessments.length
            ? report.assessments.map((a) => (
              <tr key={a.id}>
                <td className="font-medium">{TYPE_LABELS[a.assessment_type] || a.assessment_type}</td>
                <td>{a.max_marks}</td>
                <td>{a.class_average ?? '—'}</td>
                <td>{a.entry_count}</td>
                <td>{a.by_co.map((c) => `${c.co_code}: ${c.average}`).join(' · ') || '—'}</td>
              </tr>
            ))
            : [(
              <tr key="empty">
                <td colSpan="5">No assessments yet.</td>
              </tr>
            )],
        })}

        {a4TableBlocks({
          title: 'PO / PSO attainment',
          head: (
            <tr>
              <th className="bg-slate-50 w-[30%]">PO / PSO</th>
              <th className="bg-slate-50">Attainment</th>
            </tr>
          ),
          rows: poKeys.map((key) => {
            const row = program.find((p) => p.po_key === key);
            return (
              <tr key={key}>
                <td className="font-semibold">{key}</td>
                <td>{row?.percentage ?? '—'}</td>
              </tr>
            );
          }),
        })}
      </A4Document>
    </div>
  );
}
