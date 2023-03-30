from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Permission, ContentType
from rest_framework.response import Response

from meiduo_admin.serialziers.permissions import PermissionsSerializer, ContentTypeSerializer
from meiduo_admin.utils import PageNum


class PermissionsView(ModelViewSet):
    serializer_class = PermissionsSerializer
    queryset = Permission.objects.all()
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def content_type(self, request):
        """获取权限类型"""
        data = ContentType.objects.all()
        ser = ContentTypeSerializer(data, many=True)

        return Response(ser.data)
