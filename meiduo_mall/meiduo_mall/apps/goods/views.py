from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator, EmptyPage

from .models import GoodsCategory, SKU
from contents.utils import get_categories
from .utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE


# Create your views here.

class HotGoodsViews(View):
    """热销排行"""

    def get(self, request, category_id):
        # 查询指定SKU信息，必须是上架状态，销量由高到低排，最后切片取前两位
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        # 模型列表转字典列表，构造JSON数据
        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
            }
            hot_skus.append(sku_dict)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class ListViews(View):
    """商品列表页"""

    def get(self, request, category_id, page_num):
        """查询渲染商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id不存在')

        # 获取sort排序规则
        sort = request.GET.get('sort', 'default')  # 若sort没有值则取'default'
        if sort == 'price':  # 按价格升序
            sort_field = 'price'
        elif sort == 'hot':  # 按销量降序
            sort_field = '-sales'
        else:  # 默认
            sort = 'default'
            sort_field = 'create_time'
        # 获取商品分类
        categories = get_categories()
        # 获取面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 查询SKU
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)

        # 创建分页器
        paginator = Paginator(skus, 5)  # 把skus分页，每页分5个信息
        try:
            page_skus = paginator.page(page_num)  # 获取用户需要查看的页数
        except EmptyPage:
            return http.HttpResponseNotFound('Empty Page')
        total_page = paginator.num_pages  # 获取总页数

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,
            'total_page': total_page,
            'page_num': page_num,
            'sort': sort,
            'category_id': category_id,
        }
        return render(request, 'list.html', context=context)
