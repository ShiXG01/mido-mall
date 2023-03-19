from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储类"""

    def __init__(self, fdfs_base_url=None):
        # if not fdfs_base_url:
        #     self.fdfs_base_url = settings.FDFS_BASE_URL
        # self.fdfs_base_url = fdfs_base_url
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """打开文档时会调用的方法"""
        # 文档声明必须重写，但目前用不上，先pass
        pass

    def _save(self, name, content):
        """保存文件时会调用的方法"""
        # 文档声明必须重写，但目前用不上，先pass
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件相对路径
        :return: 文件全路径
        """
        return self.fdfs_base_url + name
        pass
