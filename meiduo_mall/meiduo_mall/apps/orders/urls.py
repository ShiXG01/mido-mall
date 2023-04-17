from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.InfoView.as_view(), name='info'),
    url(r'^orders/comment/$', views.CommentView.as_view()),
    url(r'^comments/(?P<sku_id>\d+)/$', views.CommentSKUView.as_view()),
    url(r'^receive/$', views.ReceiveGoodView.as_view()),
]
