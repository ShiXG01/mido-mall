from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from rest_framework.response import Response

from meiduo_admin.serialziers.admin import AdminSerializer
from meiduo_admin.serialziers.group import GroupSerializer
from meiduo_admin.utils import PageNum
from users.models import User


class AdminView(ModelViewSet):
    serializer_class = AdminSerializer
    queryset = User.objects.filter(is_staff=True)
    pagination_class = PageNum
    permission_classes = [IsAdminUser]

    def simple(self, request):
        data = Group.objects.all()
        ser = GroupSerializer(data, many=True)

        return Response(ser.data)
