import decimal
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
        random_num = str(randrange(100000, 9999999))
        print(random_num)
        upper_alpha = "ABCDEFGHJKLMNPQRSTVWXYZ"
        random_str = "".join(secrets.choice(upper_alpha) for i in range(15))
        self.code = (random_str + random_num)[-15:]
        return super().save(*args, **kwargs)

    def is_used(self):
        """
        :return: 현재 쿠폰이 사용되었는지, 사용되기 전인지를 반환 (boolean)
        """
        try:
            if self.orderhistory:
                return True
        except:
            return False

    def get_used_time(self):
        """
        :return: 쿠폰이 사용되었다면, 언제 사용되었는지를 반환
        """
        if self.is_used():
            return self.orderhistory.created_at
        else:
            return "Not used yet."

    def __str__(self):
        return f'<Coupon Objcet : {self.code}, Type : {self.coupon_type.name}>'


class CouponType(models.Model):
    """
    쿠폰 타입 모델, 퍼센트로 할인할지, 정액 할인할지, 아니면 둘 다 할인할지 등 새로운 쿠폰 타입을 생성할 수 있음
    둘 다 값이 있을 시, 퍼센트 먼저 적용 후 정가 할인 적용
    """
    name = models.CharField(max_length=20, unique=True)
    percent_discount = models.FloatField(default=0, null=True, blank=True)
    absolute_discount = models.FloatField(default=0,
                                          null=True,
                                          blank=True, )

    def save(self, *args, **kwargs):
        if self.percent_discount is None:
            self.percent_discount = 0
        if self.absolute_discount is None:
            self.absolute_discount = 0
        return super().save(*args, **kwargs)

    def get_total_discount(self):
        if self.percent_discount and self.absolute_discount:
            return float(self.percent_discount / 100), float(self.absolute_discount)
        elif self.percent_discount:
            return float(self.percent_discount / 100)
        else:
            return float(self.absolute_discount)

    def get_all_coupon_set_count(self):
        """
        :return: 해당 타입을 가지는 쿠폰의 개수를 반환
        """
        return self.coupon_set.count()

    def get_all_used_coupon_set_count(self):
        """
        :return: 해당 타입을 가지는 쿠폰 중, 사용된 것의 갯수를 반환
        """
        coupons = self.coupon_set.all()
        used_coupons = [coupon for coupon in coupons if coupon.is_used()]
        return len(used_coupons)

    def get_all_discount_results(self):
        """
        :return: 해당 쿠폰 타입으로 할인된 총액을 반환
        """
        coupons = self.coupon_set.all()
        used_coupons = [coupon for coupon in coupons if coupon.is_used()]
        all_discounts = sum([coupon.orderhistory.coupon_discount_result() for coupon in used_coupons])
        return all_discounts

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
    dilivery_price = models.FloatField(blank=True)
    # 주문 건에 대한 최종 결제가격
    total_price = models.FloatField(blank=True)
    # 사용한 쿠폰 id
    coupon = models.OneToOneField('Coupon', on_delete=models.SET_NULL, null=True, blank=True)

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

    def save(self, *args, **kwargs):
        """
        쿠폰이 있을 시, 할인가 적용
        지역, 갯수에 따른 배송비를 계산 후 저장
        할인가, 배송비에 따른 최종 결제금액 계산 후 저장

        (정상가(제품가격*개수) + 정상배송가) - (쿠폰 있을 시 할인 적용)

        임의로 정한 배송비 정책:
        country_code 의 country_decode 를 기준으로,
        코드가 1 이면 기본 배송비 10달러,
        7~90 이면 기본 배송비 15달러,
        91~299 이면 기본 배송비 20달러,
        350~599 이면 기본 배송비 25달러,
        670~692 이면 기본 배송비 30달러,
        850~998 이면 기본 배송비 35달러 차등 적용
        """

        default_price = self.product.price * self.quantity

        if self.order_place.country.country_tell_code == "1":
            default_dilivery_price = 10
            self.dilivery_price = default_dilivery_price
        elif 7 <= self.order_place.country.country_tell_code <= 90:
            default_dilivery_price = 15
            self.dilivery_price = default_dilivery_price
        elif 91 < self.order_place.country.country_tell_code <= 299:
            default_dilivery_price = 20
            self.dilivery_price = default_dilivery_price
        elif 350 <= self.order_place.country.country_tell_code <= 599:
            default_dilivery_price = 25
            self.dilivery_price = default_dilivery_price
        elif 670 <= self.order_place.country.country_tell_code <= 692:
            default_dilivery_price = 30
            self.dilivery_price = default_dilivery_price
        elif 850 <= self.order_place.country.country_tell_code <= 998:
            default_dilivery_price = 35
            self.dilivery_price = default_dilivery_price

        # 쿠폰이 있을 경우, result_price 값 할당
        if self.coupon:
            # 퍼센트 할인 적용, 정액 할인 적용이 둘 다 있는 쿠폰이라면, 정액 할인 적용 후 퍼센트 할인 적용
            if self.coupon.coupon_type.percent_discount > 0 and self.coupon.coupon_type.absolute_discount > 0:
                result_price = (default_price + default_dilivery_price - self.coupon.coupon_type.absolute_discount) * (
                        1 - self.coupon.coupon_type.percent_discount / 100)
            # 퍼센트 할인만 있는 쿠폰이라면, 퍼센트 할인만 적용
            elif self.coupon.coupon_type.percent_discount > 0 and self.coupon.coupon_type.absolute_discount == 0:
                result_price = default_price + default_dilivery_price * (
                        1 - self.coupon.coupon_type.percent_discount / 100)
            # 정액 할인만 있는 쿠폰이라면, 정액 할인만 적용
            elif self.coupon.coupon_type.percent_discount == 0 and self.coupon.coupon_type.absolute_discount > 0:
                result_price = default_price + default_dilivery_price - self.coupon.coupon_type.absolute_discount
        # 쿠폰이 없을 경우 result_price 값 할당
        else:
            result_price = default_price + default_dilivery_price

        if result_price < 0:
            self.total_price = 0
        else:
            self.total_price = result_price

        return super().save(*args, **kwargs)

    def coupon_discount_result(self):
        if self.coupon:
            default_price_with_dilivery = self.product.price * self.quantity + self.dilivery_price
            return abs(self.total_price - default_price_with_dilivery)
        else:
            return 0

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
    price = models.FloatField()

    def __str__(self):
        return f'<Product Object : {self.name}>'
