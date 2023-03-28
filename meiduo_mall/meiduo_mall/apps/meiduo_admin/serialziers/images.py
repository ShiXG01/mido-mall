from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers
from rest_framework.response import Response

from goods.models import SKUImage, SKU


class ImagesSerializer(serializers.ModelSerializer):
    """图片序列化"""

    # sku_id = serializers.IntegerField()

    class Meta:
        model = SKUImage
        fields = '__all__'

    def create(self, validated_data):
        client = Fdfs_client(settings.FASTDFS_PATH)  # 建立fastDFS连接
        # self.context['request']  获取request对象
        file = self.context['request'].FILES.get('image')
        res = client.upload_by_buffer(file.read())  # 将图片转换为二进制，用二进制方式上传
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})
        img = SKUImage.objects.create(sku=validated_data['sku'], image=res['Remote file_id'])  # 保存图片表到数据库

        return img

    def update(self, instance, validated_data):
        client = Fdfs_client(settings.FASTDFS_PATH)  # 建立fastDFS连接
        # self.context['request']  获取request对象
        file = self.context['request'].FILES.get('image')
        res = client.upload_by_buffer(file.read())  # 将图片转换为二进制，用二进制方式上传
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '图片上传失败'})
        instance.image = res['Remote file_id']
        instance.save()  # 保存图片表到数据库

        return instance


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化"""

    class Meta:
        model = SKU
        fields = ('id', 'name')
