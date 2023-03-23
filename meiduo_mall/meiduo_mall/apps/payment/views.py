import os

from alipay import AliPay
from django.conf import settings
from django.shortcuts import render
from django.views import View
from django import http

from meiduo_mall.utils.views import LoginRequiredJSONMixin
from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderInfo


# Create your views here.
from payment.models import Payment


class PaymentStatusView(LoginRequiredJSONMixin, View):
    """保存支付的订单状态"""

    def get(self, request):
        # 获取到所有的查询字符串参数
        query_dict = request.GET

        # 将查询字符串参数的类型转成标准的字典类型
        data = query_dict.dict()

        # 从查询字符串参数中提取并移除 sign，不能参与签名验证
        signature = data.pop('sign')

        # 创建SDK对象
        alipay = AliPay(  # 传入公共参数（对接任何接口都要传递的）
            appid=settings.ALIPAY_APPID,  # 应用ID
            app_notify_url=None,  # 默认回调url，如果采用同步通知就不传
            # 应用的私钥和支付宝公钥的路径
            app_private_key_string='MIIEpAIBAAKCAQEA2dkZZF+VwJvEBQL'
                                   '/GhT8UhIBLdYhHNmg1qh9WMOUwvNJMZ7yeKbelC385LRa3RGjgU1355K0u6P0ylDyH07WjbpCrKSxV'
                                   '+ndVNPAKirhCCIgZlTs8o0gvtjCqRCecruenGo+twR1qMYn/PrE8rMKY/9AWM2'
                                   '+mslaYJodo8mGEOE4Z2lHVNdP5VGmKx6D4N+xxE8cukqR0BuN6PfEmjsv'
                                   '+Tl9Xdzfn9QBeD2Fu6bTLFgZUviIDLTlr2'
                                   '+leCtmqHsPZ1UoL1TDO3SJnAyiPeoqn5es8yv8OWjYXc0OixwAGO'
                                   '/2NLLjTN2zl8V8yzpGKIDWkghT6pW8Tyk02PJ9fTbl4wIDAQABAoIBAQCBuxu3'
                                   '/oQ7s4dERMiOS7kHVtmE5mPJvoBd1PDwj2hjwGXyOunCl/0s2UYlHJKP3BU2x1+EdIVUyQraAOJvao'
                                   '+yzx0tmtZRuF+qSH/DnM1t/oS07BY/S3QYsxUZgWAai0ildU/rxagb3gWqTdxDfAPQEQ3M1JmRrB86MA0'
                                   '+oKBKI/s/PJpnl0p1sIokrb/N8twxyRuyWysABOep0awDjs4Dcr592VgJdykmIkGi3WNAgiEBXvsl'
                                   '+vEAXHaZqnGeeulmm6j'
                                   '+oY7GIn9T4YIuXUYOdVku7DCGKpRV6MRXEN3dV0gq5jSZ8Fy2s84Tf6nMI9CzBmSCIursEoO/Tik'
                                   '+NZ9BAoGBAP+mkuhKAvi37K6L+zqshPu1NEsidW5QQMg952VUQ5uSLw5Qx1jvqxj3kpWQgIJ'
                                   '/hmADoBQmU3dDY6gjleKNgkFHDV5GIIFp7fvnSmJ2ZGT8KzTCJyOX90RJ+v4/xnmp+Fvh2AV8+uMAo'
                                   '+h2Q8O1lncV0JS4eOmgLJ2N77h18Z3pAoGBANolTVJXkDAn1q6YL4JuPkFtwunC7A+4vP6ctAe14MuQui'
                                   '/DHxco9n0ajhQN3/wL5SfuSvaVPYTOqg0wryejWe/9JC'
                                   '/a6gWUOe4jymv229QY1zuHR3DYeECqO7vc5GiqY0WdTTaL7KLxb/+YfK4VUMXRwhnDrrJq'
                                   '/uatDFEHl8nrAoGAPcsknVMubrH'
                                   '+Wp5pRmBm8HR3RGX63oQ1dHFKGjsI8HSgPSSXWs7rm2hUHSTFe0WZ1GFr8xLkf+JhF0Yqt40e2'
                                   '+pxt8TZnI5fQNFCMJSPZb1yMBlx3m+gC'
                                   '/iZ25TMw6Gq74KidYklF3OTKuBTNt4QlY5HUXtZdpcJ0bd6JysTEOkCgYBncHCtrt'
                                   '+sNffSak985ZGXrNhTyB3vhoX3pY6oaVHitQnURA2mCcJ3p/PfBoVDGtDakl'
                                   '/xdOrq4qQ4BPHJNegbqElUd9WoN5UQmuANOc0bUXwduhPiKoM7Bn20oxWbm8'
                                   '/e3qwSRV88FIgrBr94PJtEciY72VIpQBsGft'
                                   '/sPFF5aQKBgQDGCa33TwcJJVcC29iVDbalIu7MUzeOfpq8jElyar9S8qxFgwd6DWHGhJMIHTT'
                                   '+F0Fi8LEvZ0B2Xa8GBTkpLrEaNJhaFTRBxhh3gtBaKpUO4YjpJvwzebupRGtcOL7AUmFfN4qUceIxqCM0Hp85DndfLWoNCfbn/G7rRkr8F2ogMA==',
            alipay_public_key_string='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkadiHKluZ/27NypsbIR9byVcrtNgf4igJ'
                                     '/wUp'
                                     '+383jcJtU7knhslqHbipv4up013ngoWd0YtNXsELfQvM28b61lJGPWW3Ei9pABKM2dngKsvXgbi0CrSk4TNCvO1nW88wyjvPbIrBmZR/I9gUUA1RhjfXb3FrnQeQBkM+cPUV8pP5aMJKJiwDdj76saVoFBgjqZYEGpMUtkEbJrc3Xsuyz3Vey3g5q3S22RGCpOFfids8/noemAep1LBIIv0jOslEGFHc7X1n7fBlZ9pVR8lHi1blxbSZLdZPtn7Fdm3731NTzAPvnpo9K+3YjKMFI6SZQJjGQQIZmqUnOGTd0UgkQIDAQAB',

            sign_type="RSA2",  # 加密标准
            debug=settings.ALIPAY_DEBUG  # 指定是否是开发环境
        )

        # 使用SDK对象，调用验通知证接口函数，得到验证结果
        success = alipay.verify(data, signature)

        # 如果验证通过，需要将支付宝的支付状态进行处理（将美多商城的订单ID和支付宝的订单ID绑定，修改订单状态）
        if success:
            # 美多商城维护的订单ID
            order_id = data.get('out_trade_no')
            # 支付宝维护的订单ID
            trade_id = data.get('trade_no')
            Payment.objects.create(
                # order = order
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单状态由"待支付"修改为"待评价"
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])

            # 响应结果
            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseForbidden('非法请求')


class PaymentView(LoginRequiredJSONMixin, View):
    """对接支付宝支付接口"""

    def get(self, request, order_id):
        """
        发起支付请求
        :param request: 请求
        :param order_id: 要支付的订单号
        :return: JSON
        """

        user = request.user
        # 校验order_id
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        # 创建对接支付宝接口的SDK对象
        alipay = AliPay(  # 传入公共参数（对接任何接口都要传递的）
            appid=settings.ALIPAY_APPID,  # 应用ID
            app_notify_url=None,  # 默认回调url，如果采用同步通知就不传
            # 应用的私钥和支付宝公钥的路径
            app_private_key_string='MIIEpAIBAAKCAQEA2dkZZF+VwJvEBQL'
                                   '/GhT8UhIBLdYhHNmg1qh9WMOUwvNJMZ7yeKbelC385LRa3RGjgU1355K0u6P0ylDyH07WjbpCrKSxV'
                                   '+ndVNPAKirhCCIgZlTs8o0gvtjCqRCecruenGo+twR1qMYn/PrE8rMKY/9AWM2'
                                   '+mslaYJodo8mGEOE4Z2lHVNdP5VGmKx6D4N+xxE8cukqR0BuN6PfEmjsv'
                                   '+Tl9Xdzfn9QBeD2Fu6bTLFgZUviIDLTlr2'
                                   '+leCtmqHsPZ1UoL1TDO3SJnAyiPeoqn5es8yv8OWjYXc0OixwAGO'
                                   '/2NLLjTN2zl8V8yzpGKIDWkghT6pW8Tyk02PJ9fTbl4wIDAQABAoIBAQCBuxu3'
                                   '/oQ7s4dERMiOS7kHVtmE5mPJvoBd1PDwj2hjwGXyOunCl/0s2UYlHJKP3BU2x1+EdIVUyQraAOJvao'
                                   '+yzx0tmtZRuF+qSH/DnM1t/oS07BY/S3QYsxUZgWAai0ildU/rxagb3gWqTdxDfAPQEQ3M1JmRrB86MA0'
                                   '+oKBKI/s/PJpnl0p1sIokrb/N8twxyRuyWysABOep0awDjs4Dcr592VgJdykmIkGi3WNAgiEBXvsl'
                                   '+vEAXHaZqnGeeulmm6j'
                                   '+oY7GIn9T4YIuXUYOdVku7DCGKpRV6MRXEN3dV0gq5jSZ8Fy2s84Tf6nMI9CzBmSCIursEoO/Tik'
                                   '+NZ9BAoGBAP+mkuhKAvi37K6L+zqshPu1NEsidW5QQMg952VUQ5uSLw5Qx1jvqxj3kpWQgIJ'
                                   '/hmADoBQmU3dDY6gjleKNgkFHDV5GIIFp7fvnSmJ2ZGT8KzTCJyOX90RJ+v4/xnmp+Fvh2AV8+uMAo'
                                   '+h2Q8O1lncV0JS4eOmgLJ2N77h18Z3pAoGBANolTVJXkDAn1q6YL4JuPkFtwunC7A+4vP6ctAe14MuQui'
                                   '/DHxco9n0ajhQN3/wL5SfuSvaVPYTOqg0wryejWe/9JC'
                                   '/a6gWUOe4jymv229QY1zuHR3DYeECqO7vc5GiqY0WdTTaL7KLxb/+YfK4VUMXRwhnDrrJq'
                                   '/uatDFEHl8nrAoGAPcsknVMubrH'
                                   '+Wp5pRmBm8HR3RGX63oQ1dHFKGjsI8HSgPSSXWs7rm2hUHSTFe0WZ1GFr8xLkf+JhF0Yqt40e2'
                                   '+pxt8TZnI5fQNFCMJSPZb1yMBlx3m+gC'
                                   '/iZ25TMw6Gq74KidYklF3OTKuBTNt4QlY5HUXtZdpcJ0bd6JysTEOkCgYBncHCtrt'
                                   '+sNffSak985ZGXrNhTyB3vhoX3pY6oaVHitQnURA2mCcJ3p/PfBoVDGtDakl'
                                   '/xdOrq4qQ4BPHJNegbqElUd9WoN5UQmuANOc0bUXwduhPiKoM7Bn20oxWbm8'
                                   '/e3qwSRV88FIgrBr94PJtEciY72VIpQBsGft'
                                   '/sPFF5aQKBgQDGCa33TwcJJVcC29iVDbalIu7MUzeOfpq8jElyar9S8qxFgwd6DWHGhJMIHTT'
                                   '+F0Fi8LEvZ0B2Xa8GBTkpLrEaNJhaFTRBxhh3gtBaKpUO4YjpJvwzebupRGtcOL7AUmFfN4qUceIxqCM0Hp85DndfLWoNCfbn/G7rRkr8F2ogMA==',
            alipay_public_key_string='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkadiHKluZ/27NypsbIR9byVcrtNgf4igJ'
                                     '/wUp'
                                     '+383jcJtU7knhslqHbipv4up013ngoWd0YtNXsELfQvM28b61lJGPWW3Ei9pABKM2dngKsvXgbi0CrSk4TNCvO1nW88wyjvPbIrBmZR/I9gUUA1RhjfXb3FrnQeQBkM+cPUV8pP5aMJKJiwDdj76saVoFBgjqZYEGpMUtkEbJrc3Xsuyz3Vey3g5q3S22RGCpOFfids8/noemAep1LBIIv0jOslEGFHc7X1n7fBlZ9pVR8lHi1blxbSZLdZPtn7Fdm3731NTzAPvnpo9K+3YjKMFI6SZQJjGQQIZmqUnOGTd0UgkQIDAQAB',

            sign_type="RSA2",  # 加密标准
            debug=settings.ALIPAY_DEBUG  # 指定是否是开发环境
        )

        # SDK对象对接支付宝支付的接口，得到登录页的地址
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 订单支付金额
            subject="美多商城%s" % order_id,  # 订单标题
            return_url=settings.ALIPAY_RETURN_URL  # 同步通知的回调地址，如果不是同步通知，就不传
        )

        # 拼接完整的支付宝登录页地址
        # 电脑网站支付(正式环境)，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 电脑网站支付(开发环境)，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
