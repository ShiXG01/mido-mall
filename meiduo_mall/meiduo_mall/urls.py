"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from django.conf.urls import url
from django.urls import re_path as url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # haystack
    url(r'^search/', include('haystack.urls')),

    url(r'^', include(('users.urls', 'users'), namespace='users')),
    url(r'^', include(('contents.urls', 'contents'), namespace='contents')),
    url(r'^', include(('verifications.urls', 'verifications'))),
    url(r'^', include(('oauth.urls', 'oauth'))),
    url(r'^', include(('areas.urls', 'areas'))),
    url(r'^', include(('goods.urls', 'goods'), namespace='goods')),
    url(r'^', include(('carts.urls', 'carts'), namespace='carts')),
    url(r'^', include(('orders.urls', 'orders'), namespace='orders')),
    url(r'^', include(('payment.urls', 'payment'), namespace='payment')),
    url(r'^meiduo_admin/', include(('meiduo_admin.urls', 'meiduo_admin'))),
]
