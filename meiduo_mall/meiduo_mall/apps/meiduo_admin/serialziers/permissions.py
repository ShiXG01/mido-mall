from rest_framework import serializers
from django.contrib.auth.models import Permission, ContentType


class PermissionsSerializer(serializers.ModelSerializer):
    """权限序列化"""

    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型序列化"""
    name = serializers.CharField(read_only=True)

    class Meta:
        model = ContentType
        fields = '__all__'
