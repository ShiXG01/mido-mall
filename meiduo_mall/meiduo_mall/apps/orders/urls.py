from django.urls import re_path as url

from . import views


urlpatterns = [
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),

]
