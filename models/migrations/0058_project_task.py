import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0057_filedownloadlog'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('unid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=160, verbose_name='Project title')),
                ('description', models.TextField(blank=True, default='',
                                                  verbose_name='Description')),
                ('color', models.CharField(
                    choices=[
                        ('#2563eb', 'Blue'), ('#059669', 'Green'), ('#dc2626', 'Red'),
                        ('#d97706', 'Amber'), ('#7c3aed', 'Purple'), ('#0891b2', 'Cyan'),
                        ('#db2777', 'Pink'), ('#65a30d', 'Lime'),
                    ],
                    default='#2563eb', max_length=10, verbose_name='Color')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('order', models.IntegerField(default=0)),
                ('is_archived', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_projects',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['order', 'created_on'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('unid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=200, verbose_name='Task title')),
                ('description', models.TextField(blank=True, default='',
                                                  verbose_name='Description')),
                ('status', models.CharField(
                    choices=[
                        ('notstarted', 'Not started'), ('inprogress', 'In progress'),
                        ('done', 'Done'), ('blocked', 'Blocked'), ('onhold', 'On hold'),
                    ],
                    default='notstarted', max_length=20)),
                ('priority', models.CharField(
                    choices=[
                        ('critical', 'Critical'), ('high', 'High'),
                        ('medium', 'Medium'), ('low', 'Low'),
                    ],
                    default='medium', max_length=20)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('order', models.IntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to='models.Project',
                )),
                ('parent_task', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subtasks',
                    to='models.Task',
                )),
                ('assigned_to', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assigned_tasks',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='created_tasks',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['order', 'created_on'],
            },
        ),
    ]
