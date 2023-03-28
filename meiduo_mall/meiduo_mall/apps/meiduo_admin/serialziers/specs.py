from rest_framework import serializers

from goods.models import SPUSpecification, SPU


class SpecsSerializer(serializers.ModelSerializer):
    """规格序列化器"""
    # 指定spu关联外键返回字段和spu_id
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化"""

    class Meta:
        model = SPU
        fields = ('id', 'name')
