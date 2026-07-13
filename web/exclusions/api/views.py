from django.conf import settings
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from exclusions.queries import get_sources, get_stats, parse_search_params, search_exclusions

from .serializers import (
    DataSourceSerializer,
    ExclusionRecordSerializer,
    StatsSerializer,
)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="firstname",
            description="Partial match on first name (AND with other name fields).",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="midname",
            description="Partial match on middle name (AND with other name fields).",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="lastname",
            description="Partial match on last name (AND with other name fields).",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="busname",
            description="Partial match on business name (AND with other name fields).",
            required=False,
            type=str,
        ),
        OpenApiParameter(
            name="npi",
            description="Exact 10-digit National Provider Identifier.",
            required=False,
            type=str,
        ),
    ]
)
class ExclusionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ExclusionRecordSerializer

    def get_queryset(self):
        params = parse_search_params(self.request.query_params)
        return search_exclusions(params)

    def paginate_queryset(self, queryset):
        page_size = self.request.query_params.get("page_size")
        if page_size:
            try:
                size = min(int(page_size), settings.API_MAX_PAGE_SIZE)
                self.paginator.page_size = size
            except ValueError:
                pass
        return super().paginate_queryset(queryset)


class SourceListView(APIView):
    def get(self, request):
        data = get_sources()
        serializer = DataSourceSerializer(data, many=True)
        return Response(serializer.data)


class StatsView(APIView):
    def get(self, request):
        data = get_stats()
        serializer = StatsSerializer(data)
        return Response(serializer.data)
