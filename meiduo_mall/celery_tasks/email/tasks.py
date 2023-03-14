# from django.core.mail import send_mail
import logging
from django.conf import settings
import smtplib
from email.mime.text import MIMEText

from celery_tasks.main import celery_app


looger = logging.getLogger('django')


# @celery_app.task(name='send_verify_email')
# bind：保证task对象作为第一个参数传入（self）
# name：任务别名
# retry_backoff：异常后自动重试的时间间隔
# max_retries：异常自动重试次数上限
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """定义发送邮件任务"""

    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为： %s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s</a></p>' % (to_email, verify_url, verify_url)

    # send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    # 构造邮件
    msg = MIMEText(html_message, 'html', 'utf-8')  # msg邮件对象
    msg['Subject'] = subject
    msg['To'] = to_email
    msg['From'] = settings.EMAIL_HOST_USER

    # 发送邮件
    try:
        ss = smtplib.SMTP_SSL('smtp.qq.com', 465)  # 465:QQ邮箱服务器的端口号
        ss.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        ss.sendmail(settings.EMAIL_HOST_USER, to_email, msg.as_string())  # 发送
        # print('邮箱发送成功！')
        return '邮箱发送成功'
    except Exception as e:
        # 触发异常自动重试,最多重试max_retries次
        raise self.retry(exec=e, max_retries=3)
        # logging.error(e)
        # # print('邮箱发送失败！详情：', e)
        # return '邮箱发送失败！详情：' + str(e)
