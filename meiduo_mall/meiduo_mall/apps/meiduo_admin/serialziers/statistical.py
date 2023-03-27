from rest_framework import serializers
from goods.models import GoodsVisitCount


class UserGoodsCountSerializer(serializers.ModelSerializer):
    # 指定嵌套序列化返回字段
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')
