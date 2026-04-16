from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0060_todo'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='scope',
            field=models.CharField(
                choices=[('personal', 'Personal'), ('shared', 'Shared')],
                default='personal',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='todo',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='todo',
            name='archived_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
