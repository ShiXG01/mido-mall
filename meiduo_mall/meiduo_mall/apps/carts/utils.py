import pickle, base64
from django_redis import get_redis_connection


def merge_carts_cookies_redis(request, response):
    """合并购物车"""
    # 获取cookie中的购物车数据
    carts_str = request.COOKIES.get('carts')

    if not carts_str:  # 判断是否有购物车cookie
        return response  # 不存在，直接返回

    cookie_carts_str_bytes = carts_str.encode()
    cookie_carts_dict_bytes = base64.b64decode(cookie_carts_str_bytes)
    cookie_cart_dict = pickle.loads(cookie_carts_dict_bytes)  # 读取购物车cookie

    new_carts_dict = {}
    new_selected_add = []
    new_selected_rem = []

    # 遍历cookies中的购物车数据
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_carts_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # 存在购物车cookie，合并
    user = request.user
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_carts_dict)
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    # 删除cookie
    response.delete_cookie('carts')
    return response
