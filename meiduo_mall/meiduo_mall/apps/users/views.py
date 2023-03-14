import json
import re
import logging

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.models import User


logger = logging.getLogger('django')


# Create your views here.

class EmailView(LoginRequiredJSONMixin, View):
    """添加邮箱"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        if not re.match(r'^[a-z\d][\w\.\-]*@[a-z\d\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('email参数有误')

        # 将邮箱保存到用户数据库的email字段中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供用户中心界面"""

        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        if request.user.is_authenticated:
            return render(request, 'user_center_info.html', context)
        else:
            return redirect(reverse('users:login'))


class LogoutView(View):
    """用户退出"""

    def get(self, requeest):
        # 结束状态保持
        logout(requeest)

        # 删除cookie中的用户名
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        return response


class LoginView(View):
    """用户登录"""

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z\d_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名不正确')
        if not re.match(r'^[\dA-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位密码')

        # 认证用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})

        login(request, user)

        # 记住用户
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        # 将用户名缓存到cookie中
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response


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

        response = redirect(reverse('contents:index'))
        # 将用户名缓存到cookie中
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # return http.HttpResponse('注册成功')
        return response
