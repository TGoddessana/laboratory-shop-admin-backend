from rest_framework.viewsets import ModelViewSet
from .models import Coupon, CouponType, OrderHistory
from .serializers import CouponSerializer, CouponTypeSerializer, OrderHistorySerializer


class OrderHistoryViewset(ModelViewSet):
    queryset = OrderHistory.objects.all()
    serializer_class = OrderHistorySerializer


class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer


class CouponTypeViewSet(ModelViewSet):
    queryset = CouponType.objects.all()
    serializer_class = CouponTypeSerializer
