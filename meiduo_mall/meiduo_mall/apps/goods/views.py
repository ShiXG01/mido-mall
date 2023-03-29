from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from datetime import datetime
import logging

from .models import GoodsCategory, SKU, GoodsVisitCount
from contents.utils import get_categories
from .utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.

logger = logging.getLogger('django')


class DetailVisitView(View):
    """统计分类商品的访问量"""

    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return render(request, '404.html')

        # 获取当前时间
        time = timezone.localtime()
        today_str = '%d-%02d-%02d' % (time.year, time.month, time.day)
        today_date = datetime.strptime(today_str, '%Y-%m-%d')

        # 统计指定分类商品的访问量
        try:
            counts_data = GoodsVisitCount.objects.get(date=today_date, category=category)
        except GoodsVisitCount.DoesNotExist:
            counts_data = GoodsVisitCount()

        try:
            counts_data.category = category
            counts_data.count += 1
            counts_data.date = today_date
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('统计失败')

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        categories = get_categories()
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return render(request, '404.html')
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)


class HotGoodsViews(View):
    """热销排行"""

    def get(self, request, category_id):
        # 查询指定SKU信息，必须是上架状态，销量由高到低排，最后切片取前两位
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:5]

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
