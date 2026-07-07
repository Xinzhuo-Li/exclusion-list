from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render

from .queries import parse_search_params, search_exclusions


def _query_string_without_page(request) -> str:
    params = request.GET.copy()
    params.pop("page", None)
    return params.urlencode()


def search_view(request):
    params = parse_search_params(request.GET)
    queryset = search_exclusions(params)
    paginator = Paginator(queryset, settings.WEB_PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "params": params,
        "page_obj": page_obj,
        "results": page_obj.object_list,
        "total_count": paginator.count,
        "query_string": _query_string_without_page(request),
        "has_search": bool(params.q or params.name or params.npi),
    }
    return render(request, "exclusions/search.html", context)
