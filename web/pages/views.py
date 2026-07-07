from django.shortcuts import render

from exclusions.queries import get_stats


def home_view(request):
    stats = get_stats()
    return render(request, "pages/home.html", {"stats": stats})


def usage_view(request):
    scheme = "https" if request.is_secure() else "http"
    base_url = f"{scheme}://{request.get_host()}"
    return render(request, "pages/usage.html", {"base_url": base_url})


def contact_view(request):
    return render(request, "pages/contact.html")
