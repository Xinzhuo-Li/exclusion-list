# Generated manually for DataSource metadata table.

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DataSource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=2, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("contributor", models.CharField(blank=True, default="", max_length=100)),
                ("record_count", models.IntegerField(default=0)),
                ("last_merged_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "ordering": ["code"],
            },
        ),
    ]
