from django.urls import path

from . import views

app_name = "algorithms"

urlpatterns = [
    path("", views.home, name="home"),
    path("explore/", views.explore, name="explore"),
    path("algorithm/<slug:slug>/", views.detail, name="detail"),
]
