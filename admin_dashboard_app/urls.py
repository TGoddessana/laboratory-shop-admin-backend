from django.urls import path, include
from rest_framework.routers import SimpleRouter
from admin_dashboard_app import views

router = SimpleRouter()
router.register("coupons", views.CouponViewSet)
router.register("coupon-types", views.CouponTypeViewSet)

urlpatterns = [
    path("", include(router.urls))
]