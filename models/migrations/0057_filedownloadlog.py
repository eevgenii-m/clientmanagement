from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0056_sharedfile_maxdownloads'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileDownloadLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=500)),
                ('referer', models.CharField(blank=True, max_length=500)),
                ('shared_file', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='download_logs',
                    to='models.SharedFile',
                )),
            ],
        ),
    ]
