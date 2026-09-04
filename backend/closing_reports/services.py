from copy import deepcopy

from attainments.models import Attainment, HistoricalCoAttainment, ProgramAttainment
from opening_reports.models import OpeningReport

from .history import dummy_values_for_year, prior_years
from .models import (
    DEFAULT_BRIGHT_ACTIONS,
    DEFAULT_WEAK_ACTIONS,
    ClosingYearSnapshot,
)


def fmt_num(value):
    if value is None or value == '':
        return ''
    try:
        return f'{float(value):.2f}'
    except (TypeError, ValueError):
        return str(value)


def _checked_labels(items, other=''):
    labels = [item.get('label') for item in (items or []) if item.get('checked') and item.get('label')]
    if other:
        labels.append(other)
    return labels


def _numeric(value):
    if value is None or value == '' or value == '-':
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def collect_history(course):
    years = prior_years(course.academic_year, 3)
    by_year = {}
    stored = set()

    snaps = ClosingYearSnapshot.objects.filter(
        course_code=course.course_code,
        semester=course.semester,
    )
    for snap in snaps:
        by_year[snap.academic_year] = {
            'cos': dict(snap.co_attainments or {}),
            'pos': dict(snap.po_attainments or {}),
            'source': snap.source,
        }
        stored.add(snap.academic_year)

    hist = HistoricalCoAttainment.objects.filter(
        course_code=course.course_code,
        semester=course.semester,
    )
    for rec in hist:
        slot = by_year.setdefault(rec.academic_year, {'cos': {}, 'pos': {}, 'source': 'COMPUTED'})
        slot['cos'][rec.co_code] = fmt_num(rec.attainment)
        stored.add(rec.academic_year)

    return years, by_year, stored


def seed_dummy_history(course):
    """Create SEED snapshots for the previous three years if none exist."""
    outcomes = list(course.outcomes.all().order_by('order', 'id'))
    po_keys = course.po_pso_keys()
    years = prior_years(course.academic_year, 3)
    created = []
    for year in years:
        cos, pos = dummy_values_for_year(year, outcomes, po_keys)
        obj, was_created = ClosingYearSnapshot.objects.get_or_create(
            course_code=course.course_code,
            academic_year=year,
            semester=course.semester,
            defaults={
                'nba_code': course.nba_code or '',
                'co_attainments': cos,
                'po_attainments': pos,
                'source': ClosingYearSnapshot.Source.SEED,
            },
        )
        if was_created:
            created.append(year)
        elif obj.source == ClosingYearSnapshot.Source.SEED and not obj.co_attainments:
            obj.co_attainments = cos
            obj.po_attainments = pos
            obj.nba_code = course.nba_code or obj.nba_code
            obj.save()
    return created, collect_history(course)


def _grade_percents_fallback():
    return [
        {'grade': g, 'pct': ''}
        for g in ('A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'F', 'I')
    ]


def build_synced(course):
    opening = OpeningReport.objects.filter(course=course).first()
    teaching = _checked_labels(
        getattr(opening, 'teaching_methods', None),
        getattr(opening, 'teaching_other', '') if opening else '',
    )
    evals = _checked_labels(
        getattr(opening, 'eval_strategies', None),
        getattr(opening, 'eval_other', '') if opening else '',
    )
    weak = [
        {'action': label, 'proof': ''}
        for label in _checked_labels(
            getattr(opening, 'weak_strategies', None),
            getattr(opening, 'weak_other', '') if opening else '',
        )
    ]
    bright = [
        {'action': label, 'proof': ''}
        for label in _checked_labels(
            getattr(opening, 'bright_strategies', None),
            getattr(opening, 'bright_other', '') if opening else '',
        )
    ]

    co_current = {}
    for att in Attainment.objects.filter(course=course).select_related('course_outcome'):
        co_current[att.course_outcome.co_code] = fmt_num(att.final_attainment)

    po_current = {}
    for pa in ProgramAttainment.objects.filter(course=course):
        po_current[pa.po_key] = fmt_num(pa.percentage)

    return {
        'teaching_methods': teaching,
        'eval_strategies': evals,
        'weak_actions': weak,
        'bright_actions': bright,
        'co_current': co_current,
        'po_current': po_current,
        'grade_percents': _grade_percents_fallback(),
        'co_targets_opening': dict(opening.co_targets) if opening and opening.co_targets else {},
        'co_actions_opening': dict(opening.co_actions) if opening and opening.co_actions else {},
    }


def target_for_co(co_code, history_by_year, opening_targets):
    manual = (opening_targets or {}).get(co_code)
    if manual not in (None, ''):
        return str(manual)
    nums = []
    for slot in (history_by_year or {}).values():
        n = _numeric((slot.get('cos') or {}).get(co_code))
        if n is not None:
            nums.append(n)
    if nums:
        return f'{round(sum(nums) / len(nums), 2):.2f}'
    return '1.80'


def mapping_checks(co, po_keys):
    mapped = {m.po_key: m.level for m in co.mappings.all()}
    checks = {}
    for key in po_keys:
        lvl = mapped.get(key)
        checks[key.lower()] = bool(lvl is not None and lvl > 0)
    return checks


def build_co8_rows(course, synced, history_by_year, years):
    po_keys = course.po_pso_keys()
    y0, y1, y2 = (years + ['', '', ''])[:3]
    rows = []
    for co in course.outcomes.all().order_by('order', 'id'):
        checks = mapping_checks(co, po_keys)
        hist_cos = lambda year: ((history_by_year.get(year) or {}).get('cos') or {}).get(co.co_code, '-')
        current = (synced.get('co_current') or {}).get(co.co_code, '')
        action = (synced.get('co_actions_opening') or {}).get(co.co_code) or ''
        if not action:
            action = 'Not Required'
        rows.append({
            'co': co.co_code,
            'a_y0': hist_cos(y0) if y0 else '-',
            'a_y1': hist_cos(y1) if y1 else '-',
            'a_y2': hist_cos(y2) if y2 else '-',
            'year_labels': [y0, y1, y2],
            'target': target_for_co(co.co_code, history_by_year, synced.get('co_targets_opening')),
            'a_current': current,
            'action': action,
            'proof': '-',
            'checks': {key: checks.get(key.lower(), False) for key in po_keys},
        })
    return rows


def build_popso9(course, synced, history_by_year):
    po_keys = course.po_pso_keys()
    out = {}
    for key in po_keys:
        target = ''
        for year in sorted(history_by_year.keys(), reverse=True):
            val = ((history_by_year[year].get('pos') or {}).get(key))
            if val not in (None, ''):
                target = str(val)
                break
        if not target:
            target = dummy_values_for_year('2023-24', [], po_keys)[1].get(key, '')
        out[key] = {
            'target': target or '',
            'attain': (synced.get('po_current') or {}).get(key, ''),
            'action': '',
            'proof': '',
        }
    return out


def hydrate_report(report, course, synced, history_by_year, years, force_tables=False):
    changed = False
    report.apply_defaults()

    def fill(field, value):
        nonlocal changed
        current = getattr(report, field)
        empty = current in (None, '', [], {})
        if empty and value:
            setattr(report, field, deepcopy(value))
            changed = True

    fill('teaching_methods', synced.get('teaching_methods'))
    fill('eval_strategies', synced.get('eval_strategies'))
    fill('weak_actions', synced.get('weak_actions'))
    fill('bright_actions', synced.get('bright_actions'))
    fill('co_current', synced.get('co_current'))
    fill('po_current', synced.get('po_current'))
    fill('grade_percents', synced.get('grade_percents'))
    if not report.weak_actions:
        report.weak_actions = deepcopy(DEFAULT_WEAK_ACTIONS)
        changed = True
    if not report.bright_actions:
        report.bright_actions = deepcopy(DEFAULT_BRIGHT_ACTIONS)
        changed = True
    if not report.teaching_methods:
        report.teaching_methods = ['']
        changed = True
    if not report.eval_strategies:
        report.eval_strategies = ['']
        changed = True
    if force_tables or not report.co8_rows:
        report.co8_rows = build_co8_rows(course, synced, history_by_year, years)
        changed = True
    if force_tables or not report.popso9:
        report.popso9 = build_popso9(course, synced, history_by_year)
        changed = True
    if not report.doc_title:
        report.doc_title = 'Course Closing Report'
        changed = True
    if changed:
        report.save()
    return changed
