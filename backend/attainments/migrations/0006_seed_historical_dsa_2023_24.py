from decimal import Decimal

from django.db import migrations


SAMPLE = [
    ('C110.1', Decimal('2.60')),
    ('C110.2', Decimal('1.30')),
    ('C110.3', Decimal('1.13')),
    ('C110.4', Decimal('1.60')),
]


def seed_historical(apps, schema_editor):
    HistoricalCoAttainment = apps.get_model('attainments', 'HistoricalCoAttainment')
    Course = apps.get_model('courses', 'Course')

    for co_code, value in SAMPLE:
        HistoricalCoAttainment.objects.update_or_create(
            course_code='17M11CS111',
            academic_year='2023-24',
            semester='ODD',
            co_code=co_code,
            defaults={
                'nba_code': 'C110',
                'attainment': value,
            },
        )

    for course in Course.objects.filter(course_code='17M11CS111'):
        changed = False
        if not getattr(course, 'department', None):
            course.department = 'Department of CSE & IT'
            changed = True
        if not course.nba_code:
            course.nba_code = 'C110'
            changed = True
        if not course.program_name:
            course.program_name = 'M.Tech (CSE)'
            changed = True
        if changed:
            course.save()


def unseed_historical(apps, schema_editor):
    HistoricalCoAttainment = apps.get_model('attainments', 'HistoricalCoAttainment')
    HistoricalCoAttainment.objects.filter(
        course_code='17M11CS111',
        academic_year='2023-24',
        semester='ODD',
        co_code__in=[row[0] for row in SAMPLE],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('attainments', '0005_historicalcoattainment'),
        ('courses', '0006_course_department'),
    ]

    operations = [
        migrations.RunPython(seed_historical, unseed_historical),
    ]
