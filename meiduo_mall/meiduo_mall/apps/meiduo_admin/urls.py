from django.urls import re_path as url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import statistical

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'statistical/total_count/$', statistical.UserCountView.as_view()),
    url(r'statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    url(r'statistical/day_orders/$', statistical.UserDayOrdersCountView.as_view()),
    url(r'statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    url(r'statistical/goods_day_views/$', statistical.UserGoodsCountView.as_view()),
    # url(r'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
