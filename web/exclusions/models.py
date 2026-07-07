from django.db import models


class ExclusionRecord(models.Model):
    """Unmanaged model mapping to ETL-owned exclusion_main table."""

    lastname = models.TextField(default="")
    firstname = models.TextField(default="")
    midname = models.TextField(default="")
    busname = models.TextField(default="")
    general = models.TextField(default="")
    specialty = models.TextField(default="")
    upin = models.CharField(max_length=6, default="")
    npi = models.CharField(max_length=10, default="")
    dob = models.CharField(max_length=8, default="")
    address = models.TextField(default="")
    city = models.TextField(default="")
    state = models.CharField(max_length=2, default="")
    zip_code = models.CharField(max_length=5, default="")
    excltype = models.TextField(default="")
    excldate = models.CharField(max_length=8, default="")
    reindate = models.CharField(max_length=8, default="")
    waiverdate = models.CharField(max_length=8, default="")
    waiverstate = models.CharField(max_length=2, default="")
    list_source = models.CharField(max_length=10, default="state")
    source_state = models.CharField(max_length=10)
    loaded_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "exclusion_main"
        ordering = ["-excldate", "id"]

    @property
    def display_name(self) -> str:
        if self.busname.strip():
            return self.busname.strip()
        parts = [self.firstname.strip(), self.midname.strip(), self.lastname.strip()]
        return " ".join(p for p in parts if p)


class DataSource(models.Model):
    """Django-managed metadata for data source coverage and contributors."""

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    contributor = models.CharField(max_length=100, blank=True, default="")
    list_source = models.CharField(max_length=10, default="state")
    record_count = models.IntegerField(default=0)
    last_merged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"
