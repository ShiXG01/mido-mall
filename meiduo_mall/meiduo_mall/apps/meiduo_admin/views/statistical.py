# 完成统计业务
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from datetime import date, timedelta

from users.models import User
from goods.models import GoodsVisitCount
from meiduo_admin.serialziers.statistical import UserGoodsCountSerializer


class UserCountView(APIView):
    """用户总量统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()  # 获取当前时间
        count = User.objects.all().count()  # 获取用户总量
        return Response({'data': now_date, 'count': count})


class UserDayCountView(APIView):
    """新增用户统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()  # 获取当前时间
        count = User.objects.filter(date_joined__gte=now_date).count()  # 获取当天注册用户总量
        return Response({'data': now_date, 'count': count})


class UserDayActiveCountView(APIView):
    """用户日活统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()  # 获取当前时间
        count = User.objects.filter(last_login__gte=now_date).count()  # 获取当天登录用户总量
        return Response({'data': now_date, 'count': count})


class UserDayOrdersCountView(APIView):
    """当日下单用户统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()  # 获取当前时间
        count = len(set(User.objects.filter(orders__create_time__gte=now_date)))  # 获取当天下单用户的总量
        return Response({'data': now_date, 'count': count})


class UserMonthCountView(APIView):
    """月增用户统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()  # 获取当前时间
        begin_date = now_date - timedelta(days=29)  # 统计的开始日期
        day_list = []
        for i in range(30):
            index_date = begin_date + timedelta(days=i)  # 获取初始日期
            next_date = begin_date + timedelta(days=i + 1)  # 获取第二天日期
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=next_date).count()
            day_list.append({
                'count': count,
                'date': index_date,
            })

        return Response(day_list)


class UserGoodsCountView(APIView):
    """日分类商品访问统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()  # 获取当前时间
        goods = GoodsVisitCount.objects.filter(date__gte=now_date)  # 获取当天分类访问量

        ser = UserGoodsCountSerializer(goods, many=True)
        return Response(ser.data)
