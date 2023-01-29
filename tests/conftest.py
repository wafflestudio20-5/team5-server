from io import BytesIO
from random import randint

import boto3
import os
import pytest
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from moto import mock_s3
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from shop.models import Brand, ProductInfo, TransProduct, StoreProduct, PurchaseBid, SalesBid


# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"
#
#
# @pytest.fixture
# def bucket_name():
#     return "my-test-bucket"
#
#
# @pytest.fixture
# def s3_client(aws_credentials, bucket_name):
#     with mock_s3():
#         s3_client = boto3.client("s3", region_name="ap-northeast-2")
#         s3_client.create_bucket(Bucket=bucket_name)
#         yield s3_client

@pytest.fixture(autouse=True)
def configure_settings(settings):
    settings.DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'


@pytest.fixture
def test_user_info():
    return 'kreamtestuser@example.com',  'kream-test-pw!', '250'


@pytest.fixture
def test_superuser_info():
    return 'kreamsuperuser@example.com',  'kream-test-pw!', '255'


@pytest.fixture
def brand(db) -> Brand:
    return Brand.objects.create(name='gucci')


@pytest.fixture
def productinfo(brand, db):
    transproduct=ProductInfo(brand=brand, eng_name='transshoe',
                             kor_name='거래 신발', delivery_tag='immediate', category='shoes')
    storeproduct = ProductInfo(brand=brand, eng_name='storebag',
                               kor_name='브랜드 가방', delivery_tag='brand', category='fashion')
    transproduct.save()
    storeproduct.save()
    return transproduct, storeproduct


@pytest.fixture
def transproducts(productinfo, db):
    SHOE_SIZE_CHOICES = [('ALL', 'ALL')] + [('{0}'.format(70 + 5 * i), '{0}'.format(70 + 5 * i)) for i in range(53)]
    bulk_list=[]
    for (i, i) in SHOE_SIZE_CHOICES:
        bulk_list.append(TransProduct.objects.create(size=i, info=productinfo[0]))
    return bulk_list


@pytest.fixture
def transproduct(productinfo, db):
    return TransProduct.objects.create(size='ALL', info=productinfo[0])


@pytest.fixture
def storeproduct(productinfo, db):
    return StoreProduct.objects.create(size='ALL', info=productinfo[1], purchase_price= 500)


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email='testuser@example.com', password='testuser!')


@pytest.fixture
def superuser(db):
    return CustomUser.objects.create_superuser(
        email='testsuperuser@example.com', password='testsuperuser!')


@pytest.fixture
def api_client_factory(db):
    def create_client(user):
        client = APIClient()
        refresh = RefreshToken.for_user(user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client
    return create_client


@pytest.fixture
def login_client(db, user, api_client_factory):
    return api_client_factory(user)

@pytest.fixture
def login_adminclient(db, superuser, api_client_factory):
    return api_client_factory(superuser)


@pytest.fixture
def purchasebids(productinfo, transproduct, user, db):
    bulk_list=[]
    for i in range(100):
        bulk_list.append(PurchaseBid.objects.create(id=i, product=transproduct, price=randint(5, 10), user=user))
    return bulk_list


@pytest.fixture
def salesbids(productinfo, transproduct,user,  db):
    bulk_list=[]
    for i in range(100):
        bulk_list.append(SalesBid.objects.create(id=i, product=transproduct, price=randint(10, 15), user=user))
    return bulk_list


@pytest.fixture
def temporary_images():
    bts, bts2 = BytesIO(), BytesIO()
    img = Image.new("RGB", (100, 100))
    img2 = Image.new("RGB", (100, 100))
    img.save(bts, 'jpeg')
    img2.save(bts, 'jpeg')
    return [SimpleUploadedFile("test.jpg", bts.getvalue()), SimpleUploadedFile("test2.jpg", bts2.getvalue())]
