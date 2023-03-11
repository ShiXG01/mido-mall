from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = 'tb_user'  # 自定义表的名字
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def _str_(self):
        return self.username, self.mobile
