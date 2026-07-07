from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exclusions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="datasource",
            name="code",
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
