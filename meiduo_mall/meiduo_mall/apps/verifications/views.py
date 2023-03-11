from django.shortcuts import render
from django.views import View
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from . import constants


# Create your views here.


class ImageCodeView(View):
    """图片验证码"""

    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return http.HttpResponse(image, content_type='image/jpg')
