import json
import re
import logging

from django import http
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_verify_email_url, check_verify_email_token
from . import constants
from goods.models import SKU
from carts.utils import merge_carts_cookies_redis

logger = logging.getLogger('django')


# Create your views here.

class UserBrowseHistory(LoginRequiredJSONMixin, View):
    """用户浏览历史"""

    def post(self, request):
        """保存用户商品浏览记录"""
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        sku_id = json_dict.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')

        redis_conn = get_redis_connection('history')
        user = request.user
        pl = redis_conn.pipeline()
        # 去重， 把与sku_id相同的历史清除
        pl.lrem('history_%s' % user.id, 0, sku_id)
        # 保存, 把sku_id存入历史列表
        pl.lpush('history_%s' % user.id, sku_id)
        # 截取, 取0到4的5个浏览历史记录
        pl.ltrim('history_%s' % user.id, 0, 4)
        # 执行
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

    def get(self, request):
        """查询用户商品浏览记录"""
        redis_conn = get_redis_connection('history')
        user = request.user
        # 取出列表数据
        sku_ids = redis_conn.lrange('history_%s' % user.id, 0, -1)

        # 查询sku_id对应的sku信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})


class UpdateTitleAddressView(LoginRequiredJSONMixin, View):
    """修改收货地址标题"""

    def put(self, request, address_id):
        """实现修改标题"""
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        if not title:
            return http.HttpResponseForbidden('缺少title')

        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新标题失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新标题成功'})


class DefaultAddressView(LoginRequiredJSONMixin, View):
    """设置默认地址"""

    def put(self, request, address_id):
        """实现默认地址设置"""
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '默认地址设置失败'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '默认地址设置成功'})


class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    """更新删除收货地址"""

    def put(self, request, address_id):
        """更新地址"""
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0\d{2,3}-)?([2-9]\d{6,7})+(-\d{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z\d][\w\.\-]*@[a-z\d\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 使用新地址覆盖旧地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})

    def deleted(self,request, address_id):
        """删除地址"""
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除数据失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除数据成功'})


class AddressCreateView(LoginRequiredJSONMixin, View):
    """新增收货地址"""

    def post(self, request):
        """实现新增地址逻辑"""

        # 判断用户地址数量是否超出上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '用户地址超出上限'})

        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0\d{2,3}-)?([2-9]\d{6,7})+(-\d{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z\d][\w\.\-]*@[a-z\d\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存用户传入的地址信息
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,  # 标题默认是收件人
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )

            # 如果用户没有默认地址，需要指定默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 响应新的地址信息给前端渲染
        # address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""

    def get(self, request):
        """查询并展示用户地址信息"""

        # 将登录用户和is_deleted作为条件查询地址数据
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        addresses_list = []
        for address in addresses:
            addresses_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            addresses_list.append(addresses_dict)

        context = {
            'default_address_id': request.user.default_address_id or 0,
            'addresses': addresses_list,
        }

        return render(request, 'user_center_site.html', context)


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return http.HttpResponseForbidden('缺少token')

        # 从token中提取用户信息
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseBadRequest('无效的token')

        # 将用户的email_active设置为Ture
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('邮箱激活失败')
        else:
            return redirect(reverse('users:info'))


class EmailView(LoginRequiredJSONMixin, View):
    """添加邮箱"""

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        if not re.match(r'^[a-z\d][\w\.\-]*@[a-z\d\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('email参数有误')

        # 将邮箱保存到用户数据库的email字段中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 发送email
        verify_url = generate_verify_email_url(request.user)
        send_verify_email.delay(email, verify_url)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    def get(self, request):
        """提供用户中心界面"""

        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        if request.user.is_authenticated:
            return render(request, 'user_center_info.html', context)
        else:
            return redirect(reverse('users:login'))


class LogoutView(View):
    """用户退出"""

    def get(self, requeest):
        # 结束状态保持
        logout(requeest)

        # 删除cookie中的用户名
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        return response


class LoginView(View):
    """用户登录"""

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z\d_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名不正确')
        if not re.match(r'^[\dA-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位密码')

        # 认证用户
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})

        login(request, user)

        # 记住用户
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))
        # 将用户名缓存到cookie中
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # 用户登录成功，合并cookie购物车到redis中
        response = merge_carts_cookies_redis(request, response)

        return response


class UsernameCountView(View):
    """判断用户是否重复注册"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class RegisterViews(View):
    """用户注册业务"""

    def get(self, request):
        """提供用户注册界面"""
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code_client = request.POST.get('sms_code')

        # 校验参数
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z\d_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名不正确')
        if not re.match(r'^[\dA-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位密码')
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '短信验证码输入错误'})

        # 保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)

        response = redirect(reverse('contents:index'))
        # 将用户名缓存到cookie中
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        # return http.HttpResponse('注册成功')
        return response
