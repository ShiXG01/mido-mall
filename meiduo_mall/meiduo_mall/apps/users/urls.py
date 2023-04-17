from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterViews.as_view(), name='register'),
    url(r'usernames/(?P<username>[a-zA-Z\d_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    url(r'^emails/$', views.EmailView.as_view()),
    url(r'^emails/verifications/$', views.VerifyEmailView.as_view()),
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    url(r'^addresses/create/$', views.AddressCreateView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
    url(r'^browse_histories/$', views.UserBrowseHistory.as_view()),
    url('^password/$', views.PwdView.as_view(), name='password'),
]
