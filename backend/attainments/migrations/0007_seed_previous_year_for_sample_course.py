from decimal import Decimal

from django.db import migrations


SAMPLE = [
    ('C110.1', Decimal('2.60')),
    ('C110.2', Decimal('1.30')),
    ('C110.3', Decimal('1.13')),
    ('C110.4', Decimal('1.60')),
]


def seed_previous_for_current_offerings(apps, schema_editor):
    """If a 17M11CS111 offering is not 2024-25, also seed its computed previous year."""
    HistoricalCoAttainment = apps.get_model('attainments', 'HistoricalCoAttainment')
    Course = apps.get_model('courses', 'Course')

    from attainments.year_utils import previous_academic_year

    years = {'2023-24'}
    for course in Course.objects.filter(course_code='17M11CS111', semester='ODD'):
        prev = previous_academic_year(course.academic_year)
        if prev:
            years.add(prev)

    for year in years:
        for co_code, value in SAMPLE:
            HistoricalCoAttainment.objects.update_or_create(
                course_code='17M11CS111',
                academic_year=year,
                semester='ODD',
                co_code=co_code,
                defaults={'nba_code': 'C110', 'attainment': value},
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('attainments', '0006_seed_historical_dsa_2023_24'),
    ]

    operations = [
        migrations.RunPython(seed_previous_for_current_offerings, noop),
    ]
