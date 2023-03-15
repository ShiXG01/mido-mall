from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^areas/$', views.AreasViews.as_view())
]