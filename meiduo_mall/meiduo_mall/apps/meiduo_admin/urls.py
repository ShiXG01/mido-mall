from django.urls import re_path as url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import statistical, users, specs, images, skus

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'statistical/total_count/$', statistical.UserCountView.as_view()),
    url(r'statistical/day_increment/$', statistical.UserDayCountView.as_view()),
    url(r'statistical/day_orders/$', statistical.UserDayOrdersCountView.as_view()),
    url(r'statistical/month_increment/$', statistical.UserMonthCountView.as_view()),
    url(r'statistical/goods_day_views/$', statistical.UserGoodsCountView.as_view()),
    # url(r'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    url(r'users/$', users.UserView.as_view()),

    url(r'goods/simple/$', specs.SpecsView.as_view({'get': 'simple'})),

    url(r'skus/simple/$', images.ImagesView.as_view({'get': 'simple'})),

    url(r'goods/(?P<pk>\d+)/specs/$', skus.SKUView.as_view({'get': 'specs'})),
]

# 自动生成路由
# 规格表路由
router = DefaultRouter()
router.register('goods/specs', specs.SpecsView, basename='specs')
# print(router.urls)
urlpatterns += router.urls

# 图片表路由
router = DefaultRouter()
router.register('skus/images', images.ImagesView, basename='images')
# print(router.urls)
urlpatterns += router.urls

# SKU路由
router = DefaultRouter()
router.register('skus', skus.SKUView, basename='skus')
# print(router.urls)
urlpatterns += router.urls
