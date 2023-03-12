from django.shortcuts import render
from django.views import View
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from . import constants
from tencentcloud.sms.v20210111 import sms_client, models
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from meiduo_mall.utils.response_code import RETCODE
import random
import json


# Create your views here.


class ImageCodeView(View):
    """图片验证码"""

    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return http.HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必要参数')
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码已失效'})
        redis_conn.delete('img_%s' % uuid)
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入的图片验证码错误'})

        sms_code = '%06d' % random.randint(0, 999999)
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 发送短信验证码
        try:
            cred = credential.Credential("AKIDCE4gDE8p0098ye8UhmhT5XmurdGgtthH", "TlsnX6e2MVYTDnALL8lETVLyPccJo69x")
            client = sms_client.SmsClient(cred, "ap-guangzhou")
            req = models.SendSmsRequest()
            params = {
                "PhoneNumberSet": ["+86"+mobile],
                "SmsSdkAppId": "1400801849",
                "SignName": "学迟轩公众号",
                "TemplateId": "1727608",
                "TemplateParamSet": [
                    sms_code
                ],
            }
            req.from_json_string(json.dumps(params))
            resp = client.SendSms(req)
        except TencentCloudSDKException as err:
            print(err)
            return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码发送失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
