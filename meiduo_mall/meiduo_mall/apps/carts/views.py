from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection
import json, base64, pickle

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


# Create your views here.

class CartsSimpleView(View):
    """简单展示商品购物车"""

    def get(self, request):
        """简单展示购物车"""
        user = request.user
        # 检查用户是否登录
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # pl = redis_conn.pipeline()
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            # pl.execute()
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected,
                }
        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:  # 判断是否有购物车cookie
                carts_str_bytes = carts_str.encode()
                carts_dict_bytes = base64.b64decode(carts_str_bytes)
                cart_dict = pickle.loads(carts_dict_bytes)  # 读取购物车cookie
            else:
                cart_dict = {}  # 新建购物车cookie

        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                'name': sku.name,
                'default_image_url': sku.default_image.url,
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})


class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        if selected:
            if not isinstance(selected, bool):  # 校验是否是bool类型
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 获取所有记录{b'14':b'1', b'1':b'1'}
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 取出字典中所有的key[b'14', b'1']
            redis_sku_ids = redis_cart.keys()

            if selected:
                # 全选
                pl.sadd('selected_%s' % user.id, *redis_sku_ids)  # *redis_sku_ids:将列表中的元素拆分放入redis
            else:
                # 取消全选
                pl.srem('selected_%s' % user.id, *redis_sku_ids)  # *redis_sku_ids:将列表中的元素拆分从redis中移除
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            carts_str = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            if carts_str:  # 判断是否有购物车cookie
                carts_str_bytes = carts_str.encode()
                carts_dict_bytes = base64.b64decode(carts_str_bytes)
                cart_dict = pickle.loads(carts_dict_bytes)  # 读取购物车cookie

                # 遍历所有购物车记录
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected

                carts_dict_bytes = pickle.dumps(cart_dict)
                carts_str_bytes = base64.b64encode(carts_dict_bytes)
                carts_str = carts_str_bytes.decode()

                response.set_cookie('carts', carts_str)
            return response


class CartsView(View):
    """购物车管理"""

    def get(self, request):
        """查询展示购物车"""
        user = request.user
        # 检查用户是否登录
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # pl = redis_conn.pipeline()
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            redis_selected = redis_conn.smembers('selected_%s' % user.id)
            # pl.execute()
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected,
                }
        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:  # 判断是否有购物车cookie
                carts_str_bytes = carts_str.encode()
                carts_dict_bytes = base64.b64decode(carts_str_bytes)
                cart_dict = pickle.loads(carts_dict_bytes)  # 读取购物车cookie
            else:
                cart_dict = {}  # 新建购物车cookie

        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })

        context = {
            'cart_skus': cart_skus,
        }

        return render(request, 'cart.html', context)

    def post(self, request):
        """保存购物车信息"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count错误')
        if selected:
            if not isinstance(selected, bool):  # 校验是否是bool类型
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hincrby('carts_%s' % user.id, sku_id, count)  # 保存商品数据
            if selected:  # 保存商品勾选状态
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录，操作cookie购物车
            carts_str = request.COOKIES.get('carts')
            if carts_str:  # 判断是否有购物车cookie
                carts_str_bytes = carts_str.encode()
                carts_dict_bytes = base64.b64decode(carts_str_bytes)
                cart_dict = pickle.loads(carts_dict_bytes)  # 读取购物车cookie
            else:
                cart_dict = {}  # 新建购物车cookie

            # 判断购物车中是否存在该商品的sku_id
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count  # 购物车中该商品数量+1

            # 刷新或增加购物车商品
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            carts_dict_bytes = pickle.dumps(cart_dict)
            carts_str_bytes = base64.b64encode(carts_dict_bytes)
            carts_str = carts_str_bytes.decode()

            # 将carts_dict写入cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            response.set_cookie('carts', carts_str)

            return response

    def put(self, request):
        """修改购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('参数count错误')
        if selected:
            if not isinstance(selected, bool):  # 校验是否是bool类型
                return http.HttpResponseForbidden('参数selected错误')

        user = request.user
        if user.is_authenticated:
            # 用户已登录
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * count)
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
        else:
            # 用户未登录
            carts_str = request.COOKIES.get('carts')
            if carts_str:  # 判断是否有购物车cookie
                carts_str_bytes = carts_str.encode()
                carts_dict_bytes = base64.b64decode(carts_str_bytes)
                cart_dict = pickle.loads(carts_dict_bytes)  # 读取购物车cookie
            else:
                cart_dict = {}  # 新建购物车cookie

            # 刷新或增加购物车商品,覆盖写入
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * count)
            }

            carts_dict_bytes = pickle.dumps(cart_dict)
            carts_str_bytes = base64.b64encode(carts_dict_bytes)
            carts_str = carts_str_bytes.decode()

            # 将carts_dict写入cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
            response.set_cookie('carts', carts_str)

            return response

    def delete(self, request):
        """删除购物车记录"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')

        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除购物车记录
            pl.hdel('carts_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录
            carts_str = request.COOKIES.get('carts')
            if carts_str:  # 判断是否有购物车cookie
                carts_str_bytes = carts_str.encode()
                carts_dict_bytes = base64.b64decode(carts_str_bytes)
                cart_dict = pickle.loads(carts_dict_bytes)  # 读取购物车cookie
            else:
                cart_dict = {}  # 新建购物车cookie

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            # 删除sku_id对应的记录
            if sku_id in cart_dict:
                del cart_dict[sku_id]  # 如果sku_id不在cart_dict中，删除会报异常

                carts_dict_bytes = pickle.dumps(cart_dict)
                carts_str_bytes = base64.b64encode(carts_dict_bytes)
                carts_str = carts_str_bytes.decode()

                # 写入新的cookie
                response.set_cookie('carts', carts_str)
            return response
