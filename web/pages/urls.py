from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("usage/", views.usage_view, name="usage"),
    path("contact/", views.contact_view, name="contact"),
]
