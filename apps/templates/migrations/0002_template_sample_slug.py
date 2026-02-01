# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("templates", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="template",
            name="sample_slug",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True, verbose_name="샘플 슬러그"),
        ),
    ]
