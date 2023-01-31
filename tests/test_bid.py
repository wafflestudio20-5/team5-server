from operator import attrgetter
from random import randint
import pytest
from django.db.models import Max, Min
from shop.models import TransProduct, SalesBid, Order, PurchaseBid


# cannot bid on all size when sizes differ
@pytest.mark.django_db
def test_purchasebid_on_all(transproducts, login_client):
    all_product_id = transproducts[0].id
    r = login_client.post(f"/shop/products/{all_product_id}/bids/?type=purchase",
                          data={"price": 500})
    assert r.status_code == 400


# cannot bid on all size when sizes differ
@pytest.mark.django_db
def test_salesbid_on_all(transproducts, login_client):
    all_product_id = transproducts[0].id
    r = login_client.post(f"/shop/products/{all_product_id}/bids/?type=sales",
                          data={"price": 500})
    assert r.status_code == 400


# purchase-sales bid on same price fails
@pytest.mark.django_db
def test_newbid_constraint(transproducts, login_client):
    bid_product_id = transproducts[1].id
    login_client.post(f"/shop/products/{bid_product_id}/bids/?type=purchase",
                      data={"price": 500})
    r = login_client.post(f"/shop/products/{bid_product_id}/bids/?type=sales",
                          data={"price": 500})
    transproducts[0].refresh_from_db()
    assert r.status_code == 400
    assert transproducts[0].purchase_price is None
    assert transproducts[0].sales_price == 500


# checking that all-sized product price always represents product prices(several sizes)
@pytest.mark.django_db
def test_allsize_price_rep(transproducts, login_client):
    for r in range(2):
        for i in transproducts:
            if i.size != 'ALL':
                login_client.post(f"/shop/products/{i.id}/bids/?type=purchase",
                                  data={"price": randint(500, 1000)})
                login_client.post(f"/shop/products/{i.id}/bids/?type=sales",
                                  data={"price": randint(1001, 1500)})
                i.refresh_from_db()
    transproducts[0].refresh_from_db()
    assert transproducts[0].sales_price == max(transproducts, key=attrgetter('sales_price')).sales_price
    assert transproducts[0].purchase_price == min(transproducts, key=attrgetter('purchase_price')).purchase_price


# checking that all-sized product price always represents product prices(one size)
@pytest.mark.django_db
def test_onesize_price_rep(transproduct, login_client):
    for i in range(10):
        login_client.post(f"/shop/products/{transproduct.id}/bids/?type=purchase",
                          data={"price": randint(500, 1000)})
        login_client.post(f"/shop/products/{transproduct.id}/bids/?type=sales",
                          data={"price": randint(1000, 2000)})
    transproduct.refresh_from_db()
    assert transproduct.sales_price == transproduct.purchasebid_set.aggregate(price=Max('price'))['price']
    assert transproduct.purchase_price == transproduct.salesbid_set.aggregate(price=Min('price'))['price']


# check if sales changes the price of object(same transproduct)
@pytest.mark.django_db
def test_transordersales(transproducts, login_client):
    login_client.post(f"/shop/products/{transproducts[1].id}/bids/?type=purchase",
                      data={"price": 500})
    login_client.post(f"/shop/products/{transproducts[1].id}/bids/?type=purchase",
                      data={"price": 600})
    login_client.post(f"/shop/products/{transproducts[1].id}/bids/?type=purchase",
                      data={"price": 400})
    transproducts[0].refresh_from_db()
    transproducts[1].refresh_from_db()
    assert transproducts[1].sales_price == 600 and transproducts[0].sales_price == 600

    login_client.post(f"/shop/products/{transproducts[1].id}/transorders/?type=sales")
    transproducts[0].refresh_from_db()
    assert transproducts[0].sales_price == 500
    login_client.post(f"/shop/products/{transproducts[1].id}/transorders/?type=sales")
    transproducts[0].refresh_from_db()
    assert transproducts[0].sales_price == 400
    login_client.post(f"/shop/products/{transproducts[1].id}/transorders/?type=sales")
    transproducts[0].refresh_from_db()
    assert transproducts[0].sales_price == None


# check if purchase changes the price of object(same transproduct)
@pytest.mark.django_db
def test_transorderpurchase(transproducts, login_client):
    login_client.post(f"/shop/products/{transproducts[1].id}/bids/?type=sales",
                      data={"price": 500})
    login_client.post(f"/shop/products/{transproducts[1].id}/bids/?type=sales",
                      data={"price": 600})
    login_client.post(f"/shop/products/{transproducts[1].id}/bids/?type=sales",
                      data={"price": 400})
    transproducts[0].refresh_from_db()
    transproducts[1].refresh_from_db()
    assert transproducts[1].purchase_price == 400 and transproducts[0].purchase_price == 400

    login_client.post(f"/shop/products/{transproducts[1].id}/transorders/?type=purchase")
    transproducts[0].refresh_from_db()
    assert transproducts[0].purchase_price == 500
    login_client.post(f"/shop/products/{transproducts[1].id}/transorders/?type=purchase")
    transproducts[0].refresh_from_db()
    assert transproducts[0].purchase_price == 600
    login_client.post(f"/shop/products/{transproducts[1].id}/transorders/?type=purchase")
    transproducts[0].refresh_from_db()
    assert transproducts[0].purchase_price == None


# check if sales changes the price of object(one transproduct)
@pytest.mark.django_db
def test_transordersales_onesize(transproduct, login_client):
    login_client.post(f"/shop/products/{transproduct.id}/bids/?type=purchase",
                      data={"price": 500})
    login_client.post(f"/shop/products/{transproduct.id}/bids/?type=purchase",
                      data={"price": 600})
    login_client.post(f"/shop/products/{transproduct.id}/bids/?type=purchase",
                      data={"price": 400})
    transproduct.refresh_from_db()
    assert transproduct.sales_price == 600 and transproduct.sales_price == 600

    login_client.post(f"/shop/products/{transproduct.id}/transorders/?type=sales")
    transproduct.refresh_from_db()
    assert transproduct.sales_price == 500
    login_client.post(f"/shop/products/{transproduct.id}/transorders/?type=sales")
    transproduct.refresh_from_db()
    assert transproduct.sales_price == 400
    login_client.post(f"/shop/products/{transproduct.id}/transorders/?type=sales")
    transproduct.refresh_from_db()
    assert transproduct.sales_price == None


# same price, earlier purchase bid gets chosen
@pytest.mark.django_db
def test_purchasebidstakenorder(transproduct, purchasebids, login_client):
    chosen_bid = sorted(purchasebids, key=lambda k: (-k.price, k.created_at))[0]
    login_client.post(f"/shop/products/{transproduct.id}/transorders/?type=sales")
    assert not PurchaseBid.objects.filter(id=chosen_bid.id).exists()


# same price, earlier sales bid gets chosen
@pytest.mark.django_db
def test_salesbidstakenorder(transproduct, salesbids, login_client):
    chosen_bid = sorted(salesbids, key=lambda k: (k.price, k.created_at))[0]
    login_client.post(f"/shop/products/{transproduct.id}/transorders/?type=purchase")
    assert not PurchaseBid.objects.filter(id=chosen_bid.id).exists()


# store order test
@pytest.mark.django_db
def test_storeorder(storeproduct, login_client):
    r = login_client.post(f"/shop/products/{storeproduct.id}/storeorders/")
    storeproduct.refresh_from_db()
    assert storeproduct.purchase_price == 500
    assert r.status_code == 201


