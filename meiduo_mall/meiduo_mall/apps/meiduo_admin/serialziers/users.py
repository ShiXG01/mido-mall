import re

from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    # 手机号判断
    def validate_mobile(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不对')
        return value

    # 重写用户保存方法
    def create(self, validated_data):
        # user = super().create(validated_data)
        # # 密码加密
        # user.set_password(validated_data['password'])
        # user.save()

        user = User.objects.create_user(**validated_data)

        return user
