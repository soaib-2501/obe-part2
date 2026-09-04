from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0006_course_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClosingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_title', models.CharField(default='Course Closing Report', max_length=255)),
                ('semester_label', models.CharField(blank=True, max_length=80)),
                ('module_coordinator', models.CharField(blank=True, max_length=255)),
                ('watermark_text', models.CharField(default='CLOSING', max_length=80)),
                ('teaching_methods', models.JSONField(blank=True, default=list)),
                ('eval_strategies', models.JSONField(blank=True, default=list)),
                ('co_current', models.JSONField(blank=True, default=dict)),
                ('po_current', models.JSONField(blank=True, default=dict)),
                ('grade_percents', models.JSONField(blank=True, default=list)),
                ('co8_rows', models.JSONField(blank=True, default=list)),
                ('popso9', models.JSONField(blank=True, default=dict)),
                ('suggestions', models.JSONField(blank=True, default=list)),
                ('weak_actions', models.JSONField(blank=True, default=list)),
                ('bright_actions', models.JSONField(blank=True, default=list)),
                ('assignment1', models.JSONField(blank=True, default=list)),
                ('practice_qs', models.JSONField(blank=True, default=list)),
                ('mini_projects', models.JSONField(blank=True, default=list)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='closing_report', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='ClosingYearSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_code', models.CharField(max_length=30)),
                ('nba_code', models.CharField(blank=True, max_length=20)),
                ('academic_year', models.CharField(max_length=20)),
                ('semester', models.CharField(choices=[('ODD', 'Odd'), ('EVEN', 'Even')], max_length=6)),
                ('co_attainments', models.JSONField(blank=True, default=dict)),
                ('po_attainments', models.JSONField(blank=True, default=dict)),
                ('source', models.CharField(choices=[('SEED', 'Dummy / seed'), ('UPLOAD', 'Uploaded'), ('COMPUTED', 'Computed from an offering')], default='SEED', max_length=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-academic_year'],
            },
        ),
        migrations.AddConstraint(
            model_name='closingyearsnapshot',
            constraint=models.UniqueConstraint(fields=('course_code', 'academic_year', 'semester'), name='unique_closing_year_snapshot'),
        ),
    ]
