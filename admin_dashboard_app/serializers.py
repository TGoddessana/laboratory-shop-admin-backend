from rest_framework import serializers
from .models import Coupon, CouponType


class CouponSerializer(serializers.ModelSerializer):
    # 해당 쿠폰의 쿠폰 타입의 id, write_only=True
    coupon_type_id = serializers.PrimaryKeyRelatedField(source='coupon_type', queryset=CouponType.objects.all())
    # 해당 쿠폰의 쿠폰 타입의 name, read_only=True
    coupon_type_name = serializers.SlugRelatedField(read_only=True, slug_field='name', source='coupon_type')
    # 쿠폰 사용내역에 대한 정보
    # {해당 쿠폰이 사용되었는가?:True or False, 해당 쿠폰이 사용된 시간은 언제인가?:사용되었다면 시간을, 아니면 "아직 사용되지 않았습니다"}
    coupon_history_info = serializers.SerializerMethodField()

    class Meta:
        model = Coupon
        fields = ["id",
                  "coupon_type_id",
                  "coupon_type_name",
                  "code",
                  "coupon_history_info"]

    def get_coupon_history_info(self, obj):
        return {"is_used": obj.is_used(), "used_time": obj.get_used_time()}


class CouponTypeSerializer(serializers.ModelSerializer):
    # % 할인 값
    percent_discount = serializers.FloatField(required=True)
    # 정액 할인 값
    absolute_discount = serializers.FloatField(required=True)
    # 쿠폰 타입의 사용내역에 관한 정보.
    coupon_type_history_info = serializers.SerializerMethodField()


    class Meta:
        model = CouponType
        fields = ["id",
                  "name",
                  "percent_discount",
                  "absolute_discount",
                  "coupon_type_history_info",]

    def get_coupon_type_history_info(self, obj):
        return {"all_coupon_set_count": obj.get_all_coupon_set_count(),
                "all_used_coupon_set_count": obj.get_all_used_coupon_set_count(),
                "all_discount_results": obj.get_all_discount_results()}
