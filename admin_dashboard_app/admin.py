from django.contrib import admin
from .models import OrderHistory, OrderPlace, Country, Coupon, CouponType, Product


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderPlace)
class OrderPlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass


@admin.register(CouponType)
class CouponTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
