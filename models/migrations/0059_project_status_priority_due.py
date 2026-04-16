from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0058_project_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(
                choices=[
                    ('active', 'Active'),
                    ('onhold', 'On hold'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='active',
                max_length=20,
                verbose_name='Status',
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='priority',
            field=models.CharField(
                choices=[
                    ('critical', 'Critical'),
                    ('high', 'High'),
                    ('medium', 'Medium'),
                    ('low', 'Low'),
                ],
                default='medium',
                max_length=20,
                verbose_name='Priority',
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='Due date'),
        ),
    ]
