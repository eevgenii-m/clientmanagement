from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import models.sharedfile as sharedfilemodel
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('models', '0054_auto_20190822_1024'),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('uplfile', models.FileField(max_length=500, upload_to=sharedfilemodel.shared_file_upload_to, verbose_name='File')),
                ('original_filename', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.CharField(blank=True, max_length=300, null=True, verbose_name='Description')),
                ('createdon', models.DateTimeField(auto_now_add=True, verbose_name='Uploaded on')),
                ('expireon', models.DateField(blank=True, null=True, verbose_name='Expires on')),
                ('downloads', models.IntegerField(default=0, verbose_name='Downloads')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='shared_files', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
