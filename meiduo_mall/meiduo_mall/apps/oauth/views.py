import re, logging
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from django.views import View
from django.conf import settings
from django import http
from django.urls import reverse
from QQLoginTool.QQtool import OAuthQQ

from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User

logger = logging.getLogger('django')


# Create your views here.

class QQAuthUserView(View):
    """处理QQ登录回调"""

    def get(self, request):
        # 获取code
        code = request.GET.get("code")
        if not code:
            return http.HttpResponseForbidden('获取code失败')

        # 使用code获取access_token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=
        settings.QQ_REDIRECT_URI)
        try:
            access_token = oauth.get_access_token(code)

            # 使用access_token获取openid
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            access_token_openid = generate_access_token(openid)
            return render(request, 'oauth_callback.html', context={'access_token_openid': access_token_openid})
        else:
            login(request, oauth_user.user)

            # 重定向到state
            next = request.GET.get('state')
            response = redirect(next)

            # 将用户名写入cookie中
            response.set_cookie('username', oauth_user.user.username, max_age=3600 * 24 * 15)

            return response

    def post(self, request):
        """实现绑定用户逻辑"""
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        # 校验参数
        if not all([password, mobile, sms_code_client]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        if not re.match(r'^[\dA-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位密码')

        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})

        # 判断openid是否有效
        openid = check_access_token(access_token_openid)
        if openid is None:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})

        # 查询手机号对应的用户是否存在
        try:
            user = User.objects.get(mobile='mobile')
        except User.DoesNotExist:  # 用户不存在
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:  # 用户存在,需要校验密码
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'account_errmsg': '账号或密码错误'})

        # 将新建用户和已存在用户进行绑定
        # oauth_qq_user = OAuthQQUser(user=user, mobile=mobile)
        # oauth_qq_user.save()
        try:
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid)
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '账号或密码错误'})

        # 实现保持状态
        login(request, oauth_qq_user.user)

        # 重定向到state
        next = request.GET.get('state')
        response = redirect(next)

        # 将用户名写入cookie中
        response.set_cookie('username', oauth_qq_user.user.username, max_age=3600 * 24 * 15)

        return response


class QQAuthURLView(View):
    """提供QQ登录扫码界面"""

    def get(self, request):
        # 接收参数
        next = request.GET.get('next')
        # 生成QQ登录扫码连接地址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=
        settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
