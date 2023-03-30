from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods
from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化"""
    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品序列化"""

    sku = SKUSerializer()

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化"""

    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
