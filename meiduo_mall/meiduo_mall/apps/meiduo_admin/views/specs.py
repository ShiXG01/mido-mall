from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from goods.models import SPUSpecification, SPU
from meiduo_admin.serialziers.specs import SpecsSerializer, SPUSerializer
from meiduo_admin.utils import PageNum


class SpecsView(ModelViewSet):
    """管理商品规格"""
    permission_classes = [IsAdminUser]
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecsSerializer
    pagination_class = PageNum

    def simple(self, request):
        """获取SPU商品信息"""
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)

        return Response(ser.data)
