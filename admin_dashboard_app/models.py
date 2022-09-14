import secrets
from random import randrange
from django.db import models


class TimeStampedModel(models.Model):
    """
    시간 저장을 위한 추상화 모델
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Coupon(models.Model):
    """
    쿠폰 모델
    """

    coupon_type = models.ForeignKey('CouponType', on_delete=models.CASCADE)
    code = models.CharField(blank=True, null=True, max_length=22)

    def save(self, *args, **kwargs):
        """
        저장시 unique 한 coupon code 생성
        """
        if self.code is None:
            random_num = str(randrange(100000,9999999))
            print(random_num)
            upper_alpha = "ABCDEFGHJKLMNPQRSTVWXYZ"
            random_str = "".join(secrets.choice(upper_alpha) for i in range(15))
            self.code = (random_str + random_num)[-15:]
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'<Coupon Objcet : {self.code}, Type : {self.coupon_type.name}>'


class CouponType(models.Model):
    """
    쿠폰 타입 모델, 퍼센트로 할인할지, 정액 할인할지, 아니면 둘 다 할인할지 등 새로운 쿠폰 타입을 생성할 수 있음
    둘 다 값이 있을 시, 퍼센트 먼저 적용 후 정가 할인 적용
    """
    name = models.CharField(max_length=20)
    percent_discount = models.FloatField(default=0, null=True, blank=True)
    absolute_discount = models.DecimalField(default=0,
                                            null=True,
                                            blank=True,
                                            max_digits=6,
                                            decimal_places=2)

    def get_total_discount(self):
        if self.percent_discount and self.absolute_discount:
            return float(self.percent_discount / 100), float(self.absolute_discount)
        elif self.percent_discount:
            return float(self.percent_discount / 100)
        else:
            return float(self.absolute_discount)

    def __str__(self):
        if self.percent_discount and self.absolute_discount:
            return f'<Coupon Type Objcet : {self.name}, {self.percent_discount}%, {self.absolute_discount}$>'
        elif self.percent_discount:
            return f'<Coupon Type Objcet : {self.name}, {self.percent_discount}%>'
        else:
            return f'<Coupon Type Objcet : {self.name}, {self.absolute_discount}$>'


class OrderHistory(TimeStampedModel):
    """
    주문내역
    """
    # 제품
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    # 결제상태 (True:결제완료 , False:결제취소)
    pay_state = models.BooleanField(default=True)
    # 제품의 수량
    quantity = models.PositiveIntegerField()
    # 배송비
    dilivery_price = models.DecimalField(max_digits=6, decimal_places=2)
    # 주문 건에 대한 최종 결제가격
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    # 사용한 쿠폰 id
    coupon = models.OneToOneField('Coupon', on_delete=models.SET_NULL, null=True)

    # 배송상태
    class DiliveryStateChoices(models.TextChoices):
        PREPARING_FOR_SHIPPING = 'preparing for shipping', '배송 준비중'
        READY_TO_SHIP = 'ready to ship', '배송 준비 완료'
        SHIPPING_IN_PROGRESS = 'shipping in progress', '배송 진행중'
        SHIPPING_COMPLETE = 'shipping complete', '배송 완료'

    dilivery_status = models.CharField(choices=DiliveryStateChoices.choices, max_length=22, blank=True)
    # 주문장소
    order_place = models.ForeignKey('OrderPlace', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'<OrderHistory Object : {self.product.name}X{self.quantity} To {self.order_place.country}, {self.total_price}$>'

    class Meta:
        verbose_name_plural = "Order Histories"


class OrderPlace(models.Model):
    """
    주문지역
    """
    # 국가
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True)
    # 도시
    city = models.CharField(max_length=150)
    # 우편번호
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return f'<OrderPlace Object : {self.country.country_name} {self.city} {self.zip_code}>'


class Country(models.Model):
    """
    국가 모델
    """
    country_name = models.CharField(max_length=100)
    country_char_code = models.CharField(max_length=2)
    country_tell_code = models.PositiveIntegerField()

    def __str__(self):
        return f'<Country Object : {self.country_name}>'

    class Meta:
        verbose_name_plural = "Countries"


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f'<Product Object : {self.name}>'
