import re
from django.contrib.auth.backends import ModelBackend
from django.conf import settings
from authlib.jose import jwt, JoseError

from users.models import User


def check_verify_email_token(token):
    """反解邮箱验证token"""
    key = settings.SECRET_KEY

    try:
        data = jwt.decode(token, key)
    except JoseError:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_verify_email_url(user):
    """生成用户验证邮箱连接"""
    header = {'alg': 'HS256'}
    key = settings.SECRET_KEY
    # 待签名的数据负载
    data = {'user_id': user.id, 'email': user.email}
    token = jwt.encode(header=header, payload=data, key=key)

    return settings.EMAIL_VERIFY_URL + '?token=' + token.decode()


def get_user_by_account(account):
    """通过账号获取用户"""
    # 判断account是用户名还是手机号
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileBackend(ModelBackend):
    """自定义用户认证"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """重写用户认证方法"""
        if request is None:
            # 后台登录
            try:
                # 查询超级管理员用户
                user = User.objects.get(username=username, is_superuser=True)
            except User.DoesNotExist:
                user = None

            if user is not None and user.check_password(password):
                return user
        else:
            # 查询用户
            user = get_user_by_account(username)

            if user and user.check_password(password):
                return user
            else:
                return None
