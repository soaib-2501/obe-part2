from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attainments', '0003_program_attainment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programattainment',
            name='po_key',
            field=models.CharField(max_length=8),
        ),
    ]
