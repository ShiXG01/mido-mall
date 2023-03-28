from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAdminUser

from meiduo_admin.serialziers.users import UserSerializer
from users.models import User
from meiduo_admin.utils import PageNum


class UserView(ListCreateAPIView):
    """获取用户数据"""
    permission_classes = [IsAdminUser]
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNum

    # 重写获取查询数据集方法
    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':  # 如果传入keyword为空，查询所有数据集
            return User.objects.all()
        else:  # 如果不为空，查询keyword指定的数据集
            return User.objects.filter(username__contains=self.request.query_params.get('keyword'))  # 模糊查询
