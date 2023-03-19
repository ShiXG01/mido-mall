from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from contents.models import ContentCategory
from contents.utils import get_categories


# Create your views here.


class IndexViews(View):

    def get(self, request):
        """提供首页广告"""
        # 获取商品分类
        categories = get_categories()

        # 查询所有广告类别
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by(
                'sequence')  # 查询未下架的广告并排序

        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context=context)

    def post(self, request):
        pass
