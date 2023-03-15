from django.shortcuts import render
from django.views import View
from django import http
from django.core.cache import cache
import logging

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE

# Create your views here.

logger = logging.getLogger('django')


class AreasViews(View):
    """省市区三级联动"""

    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            # 获取判断是否有缓存
            province_list = cache.get('province_list')
            if not province_list:
                # 查询省级数据
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)

                    # 将模型类转换成字典列表
                    province_list = []
                    for province_model in province_model_list:
                        province_dict = {
                            'id': province_model.id,
                            'name': province_model.name,
                        }
                        province_list.append(province_dict)

                    # 缓存省份字典列表信息
                    cache.set('province_list', province_list, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据查询失败'})
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
                # 查询市或区县数据
                try:
                    # 查找父类信息
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()

                    # 将模型类转换成列表字典
                    subs = []
                    for sub_model in sub_model_list:
                        sub_dict = {
                            'id': sub_model.id,
                            'name': sub_model.name,
                        }
                        subs.append(sub_dict)

                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs,
                    }

                    # 缓存城市或区县列表字典信息
                    cache.set('sub_area_' + area_id, sub_data, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区县数据查询失败'})
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
