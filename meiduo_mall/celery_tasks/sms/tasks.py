import json
import logging

from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models

from celery_tasks.main import celery_app

logger = logging.getLogger('django')


# 使用装饰器装饰异步任务，保证celery识别任务
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """发送短信验证码的异步任务"""
    # 发送短信验证码
    try:
        cred = credential.Credential("AKIDCE4gDE8p0098ye8UhmhT5XmurdGgtthH", "TlsnX6e2MVYTDnALL8lETVLyPccJo69x")
        client = sms_client.SmsClient(cred, "ap-guangzhou")
        req = models.SendSmsRequest()
        params = {
            "PhoneNumberSet": ["+86" + mobile],
            "SmsSdkAppId": "1400801849",
            "SignName": "学迟轩公众号",
            "TemplateId": "1727843",
            "TemplateParamSet": [
                sms_code
            ],
        }
        req.from_json_string(json.dumps(params))
        resp = client.SendSms(req)
        print(resp)
    except TencentCloudSDKException as err:
        # print(err)
        logger.exception(err)
        # return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '短信验证码发送失败'})
        return -1
    return 0
    # send_ret = send_sms(mobile, sms_code)
    # return send_ret
