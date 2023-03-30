from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response

from meiduo_admin.serialziers.group import GroupSerializer
from meiduo_admin.serialziers.permissions import PermissionsSerializer
from meiduo_admin.utils import PageNum


class GroupView(ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def simple(self, request):
        """获取权限数据"""
        data = Permission.objects.all()
        ser = PermissionsSerializer(data, many=True)

        return Response(ser.data)
