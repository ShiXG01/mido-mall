from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http
import random
import logging
# from tencentcloud.sms.v20210111 import sms_client, models
# from tencentcloud.common import credential
# from tencentcloud.common.exception import TencentCloudSDKException
# import json

from verifications.libs.captcha.captcha import captcha
from . import constants
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.sms.tasks import send_sms_code

# Create your views here.

logger = logging.getLogger('django')


class ImageCodeView(View):
    """图片验证码"""

    def get(self, request, uuid):
        # 生成图片验证码和文本信息
        text, image = captcha.generate_captcha()

        # 保存图片验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        return http.HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必要参数')
        redis_conn = get_redis_connection('verify_code')

        # 判断用户是否频繁发送验证码
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图片验证码已失效'})
        redis_conn.delete('img_%s' % uuid)
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入的图片验证码错误'})

        # 生成验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # 保存验证码和标记
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 发送短信验证码
        # try:
        #     cred = credential.Credential("AKIDCE4gDE8p0098ye8UhmhT5XmurdGgtthH", "TlsnX6e2MVYTDnALL8lETVLyPccJo69x")
        #     client = sms_client.SmsClient(cred, "ap-guangzhou")
        #     req = models.SendSmsRequest()
        #     params = {
        #         "PhoneNumberSet": ["+86" + mobile],
        #         "SmsSdkAppId": "1400801849",
        #         "SignName": "学迟轩公众号",
        #         "TemplateId": "1727843",
        #         "TemplateParamSet": [
        #             sms_code
        #         ],
        #     }
        #     req.from_json_string(json.dumps(params))
        #     client.SendSms(req)
        # except TencentCloudSDKException as err:
        #     # print(err)
        #     logger.exception(err)
        #     return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码发送失败'})
        send_sms_code.delay(mobile, sms_code)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})
