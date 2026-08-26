from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_description_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='program_name',
            field=models.CharField(blank=True, help_text='e.g. M.Tech CSE, B.Tech CSE', max_length=120),
        ),
        migrations.AddField(
            model_name='course',
            name='po_count',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='course',
            name='pso_count',
            field=models.PositiveSmallIntegerField(default=2),
        ),
        migrations.AlterField(
            model_name='copomapping',
            name='po_key',
            field=models.CharField(max_length=8),
        ),
    ]
