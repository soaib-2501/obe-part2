from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courses', '0006_course_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentToolsDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_title', models.CharField(default='Assessment Tools', max_length=255)),
                ('sub_heading', models.CharField(blank=True, default='Cognitive level mapping of CO to the assessment tool', max_length=255)),
                ('semester_label', models.CharField(blank=True, max_length=80)),
                ('module_coordinator', models.CharField(blank=True, max_length=255)),
                ('watermark_text', models.CharField(default='ASSESSMENT', max_length=80)),
                ('tools', models.JSONField(blank=True, default=list)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_tools', to='courses.course')),
            ],
        ),
    ]
