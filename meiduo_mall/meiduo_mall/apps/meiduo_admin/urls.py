from django.urls import re_path as url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import statistical, users, specs, images, skus, orders, permissions, group, admin

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

    url(r'permission/content_type/$', permissions.PermissionsView.as_view({'get': 'content_type'})),

    url(r'permission/simple/$', group.GroupView.as_view({'get': 'simple'})),

    url(r'permission/groups/simple/$', admin.AdminView.as_view({'get': 'simple'})),
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

# 订单路由
router = DefaultRouter()
router.register('orders', orders.OrderView, basename='orders')
# print(router.urls)
urlpatterns += router.urls

# 权限路由
router = DefaultRouter()
router.register('permission/perms', permissions.PermissionsView, basename='perms')
# print(router.urls)
urlpatterns += router.urls

# 分组路由
router = DefaultRouter()
router.register('permission/groups', group.GroupView, basename='groups')
# print(router.urls)
urlpatterns += router.urls

# 管理员路由
router = DefaultRouter()
router.register('permission/admins', admin.AdminView, basename='admin')
print(router.urls)
urlpatterns += router.urls
