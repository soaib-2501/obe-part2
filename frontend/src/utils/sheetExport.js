export function attainmentLevel(pct) {
  if (pct == null || Number.isNaN(Number(pct))) return 0;
  const n = Number(pct);
  if (n >= 80) return 3;
  if (n >= 70) return 2;
  if (n >= 60) return 1;
  return 0;
}

export function questionsForCo(questions, co) {
  const list = questions || [];
  const code = (co.co_code || '').trim().toLowerCase();
  if (code) {
    const byLabel = list.filter((q) => `${q.label || ''} ${q.key || ''}`.toLowerCase().includes(code));
    if (byLabel.length) return byLabel;
  }
  return list.filter((q) => Number(q.course_outcome) === Number(co.id));
}

export function markVal(marksGrid, studentId, questionId) {
  const raw = marksGrid[`${studentId}-${questionId}`];
  if (raw === undefined || raw === '') return null;
  const n = Number(raw);
  return Number.isNaN(n) ? null : n;
}

export function buildExamPreview({ students, block, marksGrid, outcomes }) {
  const questions = block?.questions || [];
  const target = Number(block?.target_percent) || 50;
  const useCeiling = !!block?.use_ceiling;
  const cos = (outcomes || []).filter((co) => questionsForCo(questions, co).length);

  const rows = (students || []).map((st, i) => {
    let total = 0;
    let any = false;
    const marks = {};
    questions.forEach((q) => {
      const v = markVal(marksGrid, st.id, q.id);
      marks[q.id] = v;
      if (v != null) {
        total += v;
        any = true;
      }
    });
    const coPct = {};
    cos.forEach((co) => {
      const qs = questionsForCo(questions, co);
      const maxSum = qs.reduce((s, q) => s + (Number(q.max_marks) || 0), 0);
      let sum = 0;
      let allNum = true;
      let anyE = false;
      qs.forEach((q) => {
        const v = marks[q.id];
        if (v == null) allNum = false;
        else {
          sum += v;
          anyE = true;
        }
      });
      coPct[co.id] = allNum && anyE && maxSum > 0 ? (sum / maxSum) * 100 : null;
    });
    return {
      sno: i + 1,
      enrol: st.roll_number,
      name: st.name,
      marks,
      total: any ? total : null,
      coPct,
    };
  });

  const appearedSaved = Number(block?.appeared) || 0;
  const appearedAuto = rows.filter((r) => r.total != null).length;
  const appeared = appearedSaved || appearedAuto || students.length;
  const totalStudents = Number(block?.total_students) > 0 ? Number(block.total_students) : students.length;

  const summary = cos.map((co) => {
    const qs = questionsForCo(questions, co);
    const maxSum = qs.reduce((s, q) => s + (Number(q.max_marks) || 0), 0);
    let countAtTarget = 0;
    rows.forEach((r) => {
      const pct = r.coPct[co.id];
      if (pct != null && pct >= target) countAtTarget += 1;
    });
    let pctAtTarget = appeared > 0 ? (countAtTarget / appeared) * 100 : 0;
    if (useCeiling) pctAtTarget = Math.ceil(pctAtTarget);
    return {
      co,
      maxSum,
      countAtTarget,
      pctAtTarget,
      level: attainmentLevel(pctAtTarget),
    };
  });

  return {
    questions,
    cos,
    rows,
    summary,
    target,
    appeared,
    totalStudents,
    useCeiling,
    examLabel: block?.exam_label || block?.assessment_type || '',
  };
}

export function printCurrentSheet() {
  document.body.classList.add('print-sheet-only');
  const cleanup = () => {
    document.body.classList.remove('print-sheet-only');
    window.removeEventListener('afterprint', cleanup);
  };
  window.addEventListener('afterprint', cleanup);
  window.setTimeout(() => window.print(), 80);
}

const PRINT_CSS = `
  body { font-family: Inter, Arial, sans-serif; font-size: 11px; color: #111; margin: 16px; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
  th, td { border: 1px solid #1e293b; padding: 4px 6px; }
  th { background: #f1f5f9; }
  h2, h3 { margin: 10px 0 6px; }
  .muted { color: #64748b; font-size: 10px; }
`;

export function saveNodeAsHtml(filename, node) {
  if (!node) return;
  const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${filename}</title><style>${PRINT_CSS}</style></head><body>${node.innerHTML}</body></html>`;
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename.endsWith('.html') ? filename : `${filename}.html`;
  a.click();
  URL.revokeObjectURL(a.href);
}

export function saveCsv(filename, rows) {
  const escape = (v) => {
    const s = v == null ? '' : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const csv = rows.map((row) => row.map(escape).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename.endsWith('.csv') ? filename : `${filename}.csv`;
  a.click();
  URL.revokeObjectURL(a.href);
}
