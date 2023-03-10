from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^register', views.RegisterViews.as_view(), name='register'),
    url(r'usernames/(?P<username>[a-zA-Z\d_-]{5,20})/count/$', views.UsernameCountView.as_view()),
]
