from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0063_todo_assigned_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='todo',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
