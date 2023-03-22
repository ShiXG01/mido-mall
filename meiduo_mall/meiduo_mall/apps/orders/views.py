from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from decimal import Decimal
from django import http
from django.utils import timezone
from django.db import transaction
import json

from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJSONMixin
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE


# Create your views here.

class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功页面"""

    def get(self, request):
        """提供提交订单成功页面"""
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }

        return render(request, 'order_success.html', context)
        pass


class OrderCommitView(LoginRequiredJSONMixin, View):
    """提交订单"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
            # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # 创建一个事务
        with transaction.atomic():
            # 指定数据库事务保存点
            save_id = transaction.savepoint()
            try:  # 暴力回滚
                user = request.user
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

                # 保存订单基本信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0.00),
                    freight=Decimal(8.00),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 查询redis购物车中被勾选的商品
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                redis_selected = redis_conn.smembers('selected_%s' % user.id)
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
                # 获取被勾选商品的sku_id
                sku_ids = new_cart_dict.keys()
                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)  # 查询商品和库存信息时，不能出现缓存（使用filter会出现缓存）

                        # 获取商品的原始库存和销量
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断商品库存是否充足
                        sku_count = new_cart_dict[sku.id]
                        if sku_count > sku.stock:
                            transaction.savepoint_rollback(save_id)  # 库存不足，回滚数据库
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # SKU 减库存，加销量
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if result == 0:
                            continue

                        # SPU 加销量
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单商品信息
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )

                        # 累加订单商品数量和总价到订单基本信息表中
                        order.total_count += sku_count
                        order.total_amount += sku_count * sku.price
                        break

                # 最后再加运费
                order.total_amount += order.freight
                order.save()
            except Exception:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 提交一次事务，执行数据库操作
            transaction.savepoint_commit(save_id)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """展示订单结算页面"""
        # 获取收货地址
        user = request.user
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception:
            addresses = None

        # 查询redis购物车中的勾选商品
        redis_conn = get_redis_connection('carts')
        # pl = redis_conn.pipeline()
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        redis_selected = redis_conn.smembers('selected_%s' % user.id)
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[sku_id] = int(redis_cart[sku_id])

        # 遍历new_cart_dict，取出sku_id和count
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        total_count = 0
        total_amount = Decimal(0.00)
        for sku in skus:
            sku.count = new_cart_dict[str(sku.id).encode()]
            sku.amount = sku.price * sku.count
            total_count += sku.count
            total_amount += sku.amount

        freight = Decimal(8.00)  # 邮费

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }
        return render(request, 'place_order.html', context)
