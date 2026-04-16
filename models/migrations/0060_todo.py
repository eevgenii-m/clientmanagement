from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0059_project_status_priority_due'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('status', models.CharField(
                    choices=[
                        ('todo', 'To do'),
                        ('inprogress', 'In progress'),
                        ('done', 'Done'),
                    ],
                    default='todo', max_length=20)),
                ('priority', models.CharField(
                    choices=[
                        ('high', 'High'),
                        ('medium', 'Medium'),
                        ('low', 'Low'),
                    ],
                    default='medium', max_length=20)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('order', models.IntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('completed_on', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='todos',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['order', 'created_on'],
            },
        ),
    ]
