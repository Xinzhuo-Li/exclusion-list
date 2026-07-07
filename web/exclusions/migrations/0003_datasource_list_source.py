from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("exclusions", "0002_expand_datasource_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="datasource",
            name="list_source",
            field=models.CharField(default="state", max_length=10),
        ),
    ]
