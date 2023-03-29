from django.db import transaction
from rest_framework import serializers

from goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption, SKUSpecification


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU具体规格序列化"""
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化"""

    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    specs = SKUSpecificationSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = '__all__'
        read_only_fields = ('spu', 'category')

    def create(self, validated_data):
        specs = self.context['request'].data.get('specs')
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                sku = SKU.objects.create(**validated_data)  # 保存SKU表
                for spec in specs:
                    # 保存SKU具体规格表
                    SKUSpecification.objects.create(spec_id=spec['spec_id'], option_id=spec['option_id'], sku=sku)
            except Exception:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('保存失败')
            else:
                transaction.savepoint_commit(save_point)
                return sku

    def update(self, instance, validated_data):
        specs = self.context['request'].data.get('specs')
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                SKU.objects.filter(id=instance.id).update(**validated_data)  # 修改SKU表
                for spec in specs:
                    SKUSpecification.objects.filter(sku=instance).update(**spec)  # 修改SKU具体规格表
            except Exception:
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('修改失败')
            else:
                transaction.savepoint_commit(save_point)
                return instance


class GoodsCategorySerializer(serializers.ModelSerializer):
    """分类序列化"""

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class SpecificationOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项序列化"""

    class Meta:
        model = SpecificationOption
        fields = '__all__'


class SPUSpecificationSerializer(serializers.ModelSerializer):
    """SPU规格序列化"""
    options = SpecificationOptionSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'
