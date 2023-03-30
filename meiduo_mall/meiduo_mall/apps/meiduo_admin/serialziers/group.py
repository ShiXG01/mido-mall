from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化"""
    class Meta:
        model = Group
        fields = '__all__'
