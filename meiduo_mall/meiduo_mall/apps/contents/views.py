from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from goods.models import GoodsChannel, GoodsChannelGroup, GoodsCategory
from contents.models import ContentCategory


# Create your views here.


class IndexViews(View):

    def get(self, request):
        """提供首页广告"""
        # 获取37个一级类别
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        categories = OrderedDict()

        for channel in channels:
            # 获取当前频道所在组
            group_id = channel.group_id
            # 构造数据基本框架
            if group_id not in categories:
                categories[group_id] = {'channels': [], 'sub_cats': []}
            # 查询当前频道对应的一级类别
            cat1 = channel.category
            categories[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url,
            })

            # 查询二级和三级类别
            for cat2 in cat1.subs.all():  # 用一级类别寻找二级类别
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():  # 用二级类别寻找三级类别
                    cat2.sub_cats.append(cat3)  # 将三级类别添加到二级类别的sub_cat中
                #  将二级类别添加到一级类别的sub_cat中
                categories[group_id]['sub_cats'].append(cat2)

        # 查询所有广告类别
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')  # 查询未下架的广告并排序

        context = {
            'categories': categories,
            'contents': contents,
        }

        return render(request, 'index.html', context=context)

    def post(self, request):
        pass
