from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^register$', views.RegisterViews.as_view(), name='register'),
]
