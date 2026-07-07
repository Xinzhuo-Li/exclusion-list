from rest_framework import serializers

from exclusions.models import ExclusionRecord


class ExclusionRecordSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = ExclusionRecord
        fields = [
            "id",
            "display_name",
            "lastname",
            "firstname",
            "midname",
            "busname",
            "general",
            "specialty",
            "upin",
            "npi",
            "dob",
            "address",
            "city",
            "state",
            "zip_code",
            "excltype",
            "excldate",
            "reindate",
            "waiverdate",
            "waiverstate",
            "list_source",
            "source_state",
            "loaded_at",
        ]


class DataSourceSerializer(serializers.Serializer):
    code = serializers.CharField()
    name = serializers.CharField()
    contributor = serializers.CharField()
    record_count = serializers.IntegerField()
    last_merged_at = serializers.CharField(allow_null=True)


class SourceStateStatSerializer(serializers.Serializer):
    source_state = serializers.CharField()
    name = serializers.CharField()
    count = serializers.IntegerField()


class StatsSerializer(serializers.Serializer):
    total_records = serializers.IntegerField()
    source_count = serializers.IntegerField()
    by_source_state = SourceStateStatSerializer(many=True)
