from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from goods.models import SKU, GoodsCategory, SPU
from meiduo_admin.utils import PageNum

from meiduo_admin.serialziers.skus import SKUSerializer, GoodsCategorySerializer, SPUSpecificationSerializer


class SKUView(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = PageNum

    # 重写获取查询集数据的方法
    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return SKU.objects.all()
        elif self.request.query_params.get('keyword') is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=self.request.query_params.get('keyword'))

    @action(methods=['get'], detail=False)
    def categories(self, reques):
        """获取商品三级分类"""
        data = GoodsCategory.objects.filter(subs=None)
        ser = GoodsCategorySerializer(data, many=True)
        return Response(ser.data)

    def specs(self, request, pk):
        """获取SPU商品规格信息"""
        spu = SPU.objects.get(id=pk)
        data = spu.specs.all()
        ser = SPUSpecificationSerializer(data, many=True)
        return Response(ser.data)
