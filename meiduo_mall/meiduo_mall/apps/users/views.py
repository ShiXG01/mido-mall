from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django import http
from django.db import DatabaseError
from django_redis import get_redis_connection
import re

from users.models import User
from meiduo_mall.utils.response_code import RETCODE


# Create your views here.

class UsernameCountView(View):
    """判断用户是否重复注册"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterViews(View):
    """用户注册业务"""

    def get(self, request):
        """提供用户注册界面"""
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 校验参数
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z\d_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名不正确')
        if not re.match(r'^[\dA-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位密码')
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码输入错误'})

        # 保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)

        # return http.HttpResponse('注册成功')
        return redirect(reverse('contents:index'))
