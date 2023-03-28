from django.conf import settings
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from fdfs_client.client import Fdfs_client

from goods.models import SKUImage, SKU
from meiduo_admin.serialziers.images import ImagesSerializer, SKUSerializer
from meiduo_admin.utils import PageNum


class ImagesView(ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = PageNum

    def simple(self, request):
        """获取sku商品"""
        skus = SKU.objects.all()
        ser = SKUSerializer(skus, many=True)

        return Response(ser.data)

    # def create(self, request, *args, **kwargs):
    #     data = request.data  # 获取前端数据
    #     ser = self.get_serializer(data=data)
    #     ser.is_valid()  # 验证数据
    #     # client = Fdfs_client(settings.FASTDFS_PATH)  # 建立fastDFS连接
    #     # file = request.FILES.get('image')
    #     # res = client.upload_by_buffer(file.read())  # 将图片转换为二进制，用二进制方式上传
    #     # if res['Status'] != 'Upload successed.':
    #     #     return Response({'error': '图片上传失败'})
    #     # img = SKUImage.objects.create(sku=ser.validated_data['sku'], image=res['Remote file_id'])  # 保存图片表到数据库
    #
    #     ser.save()
    #
    #     return Response(ser.data, status=201)
