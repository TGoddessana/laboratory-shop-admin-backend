from rest_framework.viewsets import ModelViewSet
from .models import Coupon, CouponType
from .serializers import CouponSerializer, CouponTypeSerializer


class CouponViewSet(ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer


class CouponTypeViewSet(ModelViewSet):
    queryset = CouponType.objects.all()
    serializer_class = CouponTypeSerializer
