from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0055_sharedfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='sharedfile',
            name='max_downloads',
            field=models.IntegerField(blank=True, null=True, verbose_name='Maximum downloads'),
        ),
    ]
