from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from orders.models import OrderInfo
from meiduo_admin.utils import PageNum
from meiduo_admin.serialziers.orders import OrderSerializer


class OrderView(ReadOnlyModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    pagination_class = PageNum

    def get_queryset(self):
        if self.request.query_params.get('keyword') == '':
            return OrderInfo.objects.all()
        elif self.request.query_params.get('keyword') is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=self.request.query_params.get('keyword'))

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """修改订单状态"""
        try:
            order = OrderInfo.objects.get(order_id=pk)
        except Exception:
            return Response({'error': '订单编号错误'})

        status = request.data.get('status')
        if status == '' or status is None:
            return Response({'error': '缺少状态值'})
        order.status = status
        order.save()

        return Response({
            'order_id': pk,
            'status': status
        })
