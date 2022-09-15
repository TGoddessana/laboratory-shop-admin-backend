from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import Client
from admin_dashboard_app.models import Coupon, CouponType, OrderHistory, Country, OrderPlace, Product


class OrderHistoryTests(APITestCase):
    """
    주문목록에 대한 기능을 테스트합니다.
    1. 주문 목록에 대해서 GET 요청을 보냄으로서, 주문 목록을 조회할 수 있습니다.
        1-1. 주문 목록은 5개를 생성할 것이므로, 응답의 길이는 5가 되어야 합니다.
        1-2. 주문 목록의 첫 번째 데이터를 살펴보면, 아래와 같습니다.

                self.orderhistory_1 = OrderHistory(product=self.product_1,
                                           order_place=self.order_place_1,
                                           pay_state=False,
                                           quantity=99,
                                           coupon=self.coupon_1)

                제품은 299000 달러이고,
                주문지역 국가의 국가 코드는 1이며,
                양은 99개,
                쿠폰은 50%를 할인해 주고 있습니다.
                만약 의도한 대로 최종 결제금액 코드가 작동한다면,
                최종 결제가격은 계산에 의해 아래와 같아야 합니다.
                (제품의 가격 * 개수 + 기본 배송비) * 할인쿠폰 적용
                (299000*99 + 10) * (1 - 0.9) = 2960100.9999999995
                1번 주문내역의 total_price 가 위와 같은지 검증합니다.

    2. 주문 상세에 대해서 GET 요청을 보냄으로서, 주문 상세내용을 조회할 수 있습니다.
       2-1. 주문 목록의 세 번째 데이터를 살펴보면, 아래와 같습니다.
            같은 serializer 를 사용하고 있으므로, 계산은 똑같이 들어갔다고 가정합니다.
            직렬화 과정에서, 제품의 id 대신 이름인 "Damas" 가 나타나는지 검증합니다.
            의도되지 않은 응답 키인 "product_id" 가 응답에 나타나지 않는지 검증합니다.

    3. 주문 목록에 대해서 POST 요청을 보내면, 새로운 주문 조회를 생성합니다.
       보내는 데이터에 "어떤 제품을", "어떤 장소에서", "어떤 쿠폰을 사용하여", "몇 개를 주문하는지" 를 입력하면,
       자동으로 "지역에 따른 배송비", "할인가" 를 계산하여 "최종 결제가격" 을 데이터베이스에 저장합니다.
       기존의 5개에 추가된 1개를 더해서, 최종적으로 주문내역은 6개가 되어야 합니다.

    4. 특정 주문에 대해서 PUT 요청을 보냄으로서, 주문에 대해서 수정을 할 수 있습니다.
       "결제 상태", "배송 상태" 등을 바꿀 수 있습니다.
       테스트 코드에서는 1번 주문내역의 "결제 상태" 를 False 에서 True로 바꾸고,
       해당 주문내역 상세에 대한 GET 메서드를 요청하여 pay_state 가 True로 바뀌었는지 확인합니다.

    5. 특정 주문에 대해서 DELETE 요청을 보냄으로서, 주문에 대해서 삭제를 할 수 있습니다.
       1번 주문내역에 DELETE 요청을 보낸 후, 1번 주문내역 상세에 대해서 GET 요청을 보냅니다.
       해당 요청의 상태 코드가 리소스를 찾을 수 없다는 404인지 확인합니다.
    """

    def setUp(self):
        """
        테스트를 위한 사전 준비
        1. 클라이언트 생성
        2. 나라 데이터 생성, 쿠폰 타입 데이터 생성, 쿠폰 데이터 생성, 주문장소 데이터 생성, 제품 데이터 생성
           쿠폰 데이터 생성 시, 타입만 지정해 준다면 unique 한 코드는 자동으로 생성됩니다.
        3. 주문 목록 데이터 생성
        """

        # 요청을 위한 클라이언트 생성
        self.client = Client()

        # 나라 데이터 생성
        self.country_usa = Country(country_name="USA",
                                   country_char_code="US",
                                   country_tell_code=1)
        self.country_usa.save()
        self.country_kor = Country(country_name="KOREA",
                                   country_char_code="KR",
                                   country_tell_code=82)
        self.country_kor.save()
        self.country_lao = Country(country_name="LAOS",
                                   country_char_code="LA",
                                   country_tell_code=856)
        self.country_lao.save()

        # 쿠폰 타입 데이터 생성
        self.coupon_type_1 = CouponType(name="블랙 프라이데이 할인",
                                        percent_discount=90,
                                        absolute_discount=0)
        self.coupon_type_1.save()
        self.coupon_type_2 = CouponType(name="어린이날 할인",
                                        percent_discount=0,
                                        absolute_discount=55)
        self.coupon_type_2.save()
        self.coupon_type_3 = CouponType(name="빼빼로데이 할인",
                                        percent_discount=11,
                                        absolute_discount=11)
        self.coupon_type_3.save()

        # 쿠폰 데이터 생성
        self.coupon_1 = Coupon(coupon_type_id=1)
        self.coupon_1.save()
        self.coupon_2 = Coupon(coupon_type_id=2)
        self.coupon_2.save()
        self.coupon_3 = Coupon(coupon_type_id=2)
        self.coupon_3.save()
        self.coupon_4 = Coupon(coupon_type_id=3)
        self.coupon_4.save()
        self.coupon_5 = Coupon(coupon_type_id=3)
        self.coupon_5.save()

        # 주문장소 데이터 생성
        self.order_place_1 = OrderPlace(country=self.country_usa,
                                        city="Los Angeles",
                                        zip_code="90000")
        self.order_place_1.save()
        self.order_place_2 = OrderPlace(country=self.country_kor,
                                        city="Seoul",
                                        zip_code="01878")
        self.order_place_2.save()
        self.order_place_3 = OrderPlace(country=self.country_lao,
                                        city="Vientiane",
                                        zip_code="0604")
        self.order_place_3.save()

        # 제품 데이터 생성
        self.product_1 = Product(name="Phantom Series II",
                                 price=299000)
        self.product_1.save()
        self.product_2 = Product(name="Damas",
                                 price=500)
        self.product_2.save()
        self.product_3 = Product(name="Sonata",
                                 price=1350)
        self.product_3.save()

        # 주문목록 데이터 생성
        self.orderhistory_1 = OrderHistory(product=self.product_1,
                                           order_place=self.order_place_1,
                                           pay_state=False,
                                           quantity=99,
                                           coupon=self.coupon_1)
        self.orderhistory_1.save()
        self.orderhistory_2 = OrderHistory(product=self.product_2,
                                           order_place=self.order_place_1,
                                           pay_state=False,
                                           quantity=1,
                                           coupon=self.coupon_2)
        self.orderhistory_2.save()
        self.orderhistory_3 = OrderHistory(product=self.product_2,
                                           order_place=self.order_place_2,
                                           pay_state=False,
                                           quantity=3,
                                           coupon=self.coupon_3)
        self.orderhistory_3.save()
        self.orderhistory_4 = OrderHistory(product=self.product_3,
                                           order_place=self.order_place_3,
                                           pay_state=False,
                                           quantity=10,
                                           coupon=self.coupon_4)
        self.orderhistory_4.save()
        self.orderhistory_5 = OrderHistory(product=self.product_3,
                                           order_place=self.order_place_3,
                                           pay_state=False,
                                           quantity=20,
                                           coupon=self.coupon_5)
        self.orderhistory_5.save()

    def test_getmethod_orderhistories_list(self):
        self.url = reverse('orderhistory-list')
        response = self.client.get(self.url)
        # 5개의 주문내역을 생성했으므로, 응답의 길이는 총 5개가 되어야 합니다.
        self.assertEqual(5, len(response.data))
        # 가격은 제대로 계산되어서 들어가야 합니다.
        self.assertEqual(2960100.9999999995, (dict(response.data[0])['total_price']))

    def test_getmethod_orderhistories_detail(self):
        self.url = reverse('orderhistory-list')
        # 3번 주문내역의 결과를 조회합니다.
        response = self.client.get(f'{self.url}3/')
        # 요청의 값들 중에, 제품의 이름인 "Damas" 가 존재하는지 확인합니다.
        self.assertIn('Damas', response.data.values())
        # 요청의 키들 중에, 의도되지 않은 키인 "product_id" 가 존재하지 않는지 확인합니다.
        self.assertNotIn('product_id', response.data.keys())

    def test_postmethod_orderhistories_list(self):
        self.url = reverse('orderhistory-list')
        # 아래의 데이터로 임의의 주문내역을 생성합니다.
        # 최종 결제가격은, (299000*1 + 10) * 1 = 299010 이 되어야 합니다.
        response = self.client.post(f'{self.url}',
                                    data={
                                        "pay_state": False,
                                        "quantity": 1,
                                        "dilivery_status": 'preparing for shipping',
                                        "product_id": 1,
                                        "coupon": "",
                                        "order_place_id": 1
                                    })
        # 저장이 잘 되었는지를 확인합니다.
        self.assertEqual(201, response.status_code)
        # 가격이 잘 계산되어 저장되었는지를 확인합니다.
        self.assertEqual(299010, response.data["total_price"])
        # 주문목록에 대해서 get 요청을 보내서, 총 응답이 원래의 5개에 1개가 더해진 6개가 맞는지를 확인합니다.
        response = self.client.get(self.url)
        self.assertEqual(6, len(response.data))

    def test_putmethod_orderhistories_list(self):
        self.url = reverse('orderhistory-list')
        # 아래의 데이터로 1번 주문내역을 수정합니다.
        # 수정 후, 데이터가 원하는 대로 수정되었는지 확인합니다.
        response = self.client.put(f'{self.url}1/',
                                   data={
                                       "pay_state": True,
                                       "quantity": 99,
                                       "dilivery_status": 'preparing for shipping',
                                       "product_id": 2,
                                       "coupon": "1",
                                       "order_place_id": 1
                                   },
                                   follow=True,
                                   content_type="application/json", )
        response = self.client.get(f'{self.url}1/')
        # 수정한 "pay_state" 가 False에서 True로 잘 변경되었는지 확인합니다.
        self.assertEqual(True, response.data['pay_state'])

    def test_deletemethod_orderhistories_list(self):
        self.url = reverse('orderhistory-list')
        # 삭제 요청을 보냅니다.
        response = self.client.delete(f'{self.url}1/')
        # 삭제가 제대로 이루어지고, 서버는 해당 상태 코드인 204를 응답해주는지 확인합니다.
        self.assertEqual(204, response.status_code)
        # 삭제된 주문내역의 상세에 GET 요청을 보내고, 해당 요청의 상태 코드가 404와 같은지 확인합니다.
        response = self.client.get(f'{self.url}1/')
        self.assertEqual(404, response.status_code)

