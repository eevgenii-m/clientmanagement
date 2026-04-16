import uuid
import models.uploadlink
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def calc_expiry_upload():
    from datetime import datetime, timedelta
    return datetime.today().date() + timedelta(days=7)

def upload_to_client(instance, filename):
    import os
    return os.path.join('client_uploads', instance.unid.hex, filename)

class Migration(migrations.Migration):
    dependencies = [
        ('models', '0061_todo_scope_archive'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='UploadLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=120, verbose_name='Title / Purpose')),
                ('description', models.TextField(blank=True, default='', verbose_name='Instructions for client')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('expires_on', models.DateField(default=calc_expiry_upload)),
                ('is_active', models.BooleanField(default=True)),
                ('max_files', models.IntegerField(default=10)),
                ('created_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.CreateModel(
            name='ClientUploadedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uplfile', models.FileField(max_length=255, upload_to=upload_to_client)),
                ('original_filename', models.CharField(max_length=255)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('file_size', models.BigIntegerField(default=0)),
                ('upload_link', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='uploaded_files',
                    to='models.uploadlink',
                )),
            ],
        ),
    ]