from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListViews.as_view(), name='list'),
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsViews.as_view()),
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),
]
