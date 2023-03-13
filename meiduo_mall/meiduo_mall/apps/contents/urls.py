from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^$', views.IndexViews.as_view(), name='index'),
    url(r'^index/$', views.IndexViews.as_view()),
]
