from django.contrib.auth import get_user_model
from django.core.exceptions import FieldError
from django.db.models import Count, Sum, Min
from rest_framework import serializers
import shop
from accounts.models import CustomUser
from shop.models import ProductInfo, Brand, Wish, TransProduct, StoreProduct, TransOrder, StoreOrder, PurchaseBid, \
    SalesBid, Order


class ProductInfoSerializer(serializers.ModelSerializer):
    productimage_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    price = serializers.SerializerMethodField()
    wishes = serializers.SerializerMethodField()
    shares = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name', 'delivery_tag', 'productimage_set', 'price', 'shares',
                  'wishes']

    def get_price(self, obj: ProductInfo):
        if obj.delivery_tag == 'immediate':
            return obj.transproduct_set.aggregate(price=Min('purchase_price'))['price']
        return obj.storeproduct_set.aggregate(price=Min('purchase_price'))['price']

    def get_wishes(self, obj: ProductInfo):
        if obj.delivery_tag == 'immediate':
            return sum(i.wish_set.count() for i in obj.transproduct_set.all())
        return sum(i.wish_set.count() for i in obj.storeproduct_set.all())

    def get_shares(self, obj: ProductInfo):
        return obj.share_set.all().count()


class TransProductListSerializer(serializers.ModelSerializer):
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES + shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = TransProduct
        fields = ['id', 'size', 'sales_price', 'purchase_price', ]
        read_only_fields = ['sales_price', 'purchase_price']

    def validate_size(self, size):
        if TransProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size

    def create(self, validated_data):
        validated_data['info'] = ProductInfo.objects.get(id=self.context['view'].kwargs['info'])
        instance = super().create(validated_data)
        return instance


class StoreProductListSerializer(serializers.ModelSerializer):
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES + shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = StoreProduct
        fields = ['id', 'size', 'purchase_price']

    def validate_size(self, size):
        if StoreProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size

    def create(self, validated_data):
        validated_data['info'] = ProductInfo.objects.get(id=self.context['view'].kwargs['info'])
        instance = super().create(validated_data)
        return instance


class TransProductDetailSerializer(serializers.ModelSerializer):
    info = ProductInfoSerializer(read_only=True)
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES + shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = TransProduct
        fields = ['id', 'size', 'purchase_price', 'purchase_price', 'info']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_anonymous:
            wishcheck = False
        elif Wish.objects.filter(user=user, product=instance).exists():
            wishcheck = True
        else:
            wishcheck = False

        res.setdefault('user_wishcheck', wishcheck)
        return res

    def validate_size(self, size):
        if TransProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size


class StoreProductDetailSerializer(serializers.ModelSerializer):
    info = ProductInfoSerializer(read_only=True)
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES + shop.models.CLOTHES_SIZE_CHOICES)
    size_options = serializers.SerializerMethodField(allow_null=True)

    class Meta:
        model = StoreProduct
        fields = ['id', 'size', 'purchase_price', 'info', 'size_options']

    def get_size_options(self, obj: StoreProduct):
        return [i.size for i in StoreProduct.objects.filter(info=obj.info) if i.size != 'ALL']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_anonymous:
            wishcheck = False
        elif Wish.objects.filter(user=user, product=instance).exists():
            wishcheck = True
        else:
            wishcheck = False
        res.setdefault('user_wishcheck', wishcheck)
        return res

    def validate_size(self, size):
        if StoreProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']


class TransSizeWishSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransProduct
        fields = ['id', 'size', 'purchase_price']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        wishcheck = False
        if Wish.objects.filter(user=user, product=instance).exists():
            wishcheck = True
        res.setdefault('user_wishcheck', wishcheck)
        return res


class StoreSizeWishSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreProduct
        fields = ['id', 'size', 'purchase_price']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        wishcheck = False
        if Wish.objects.filter(user=user, product=instance).exists():
            wishcheck = True
        res.setdefault('user_wishcheck', wishcheck)
        return res


class TransOrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TransOrder
        fields = ['id', 'buyer', 'seller', 'product', 'price', 'product_engname', 'size', 'created_at']
        read_only_fields = ['price', 'product_engname', 'size', 'created_at']

    def create(self, validated_data):
        product = self.context['product']
        if product.size=='ALL':
            raise serializers.ValidationError({
                'size': 'cannot order ALL size products'
            })
        bid = self.context['bid']
        if self.context['transaction_type'] == 'purchase':
            validated_data['price'] = product.purchase_price
            validated_data['buyer'] = self.context['user']
            validated_data['seller'] = bid.user
        else:
            validated_data['price'] = product.sales_price
            validated_data['seller'] = self.context['user']
            validated_data['buyer'] = bid.user
        validated_data['product'] = product
        validated_data['product_engname'] = product.info.eng_name
        validated_data['size'] = product.size
        bid.delete()
        instance = super().create(validated_data)
        return instance


class StoreOrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = StoreOrder
        fields = ['id', 'store', 'buyer', 'product', 'price', 'product_engname', 'size']
        read_only_fields = ['price', 'product_engname', 'size', 'created_at']

    def create(self, validated_data):
        product = self.context['product']
        if product.size == 'ALL':
            raise serializers.ValidationError({
                'size': 'cannot order ALL size products'
            })
        validated_data['store'] = product.info.brand
        validated_data['buyer'] = self.context['user']
        validated_data['product'] = product
        validated_data['price'] = product.purchase_price
        validated_data['product_engname'] = product.info.eng_name
        validated_data['size'] = product.size
        instance = super().create(validated_data)
        return instance


class OrderListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format='%Y/%m/%d')

    class Meta:
        model = Order
        fields = ['id', 'product', 'price', 'size', 'created_at']


class PurchaseBidListSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = PurchaseBid
        fields = ['id', 'price', 'count']

    def to_internal_value(self, data):
        product = self.context['product']
        user = self.context['user']
        price = int(data['price'])
        if product.size == 'ALL':
            raise serializers.ValidationError({
                'size': 'cannot bid on ALL size products'
            })
        if product.purchase_price and price >= product.purchase_price:
            raise serializers.ValidationError({"price": "purchase bid should be less than the current purchase_price of "
                                                        "the product."})
        return {
            'product': product,
            'user': user,
            'price': price
        }


class SalesBidListSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SalesBid
        fields = ['id', 'price', 'count']

    def to_internal_value(self, data):
        product = self.context['product']
        user = self.context['user']
        price = int(data['price'])
        if product.size == 'ALL':
            raise serializers.ValidationError({
                'size': 'cannot bid on ALL size products'
            })
        if product.sales_price and price <= product.sales_price:
            raise serializers.ValidationError({"price": "sales bid should be more than the current purchase_price of "
                                                        "the product."})
        return {
            'product': product,
            'user': user,
            'price': price
        }


class PurchaseBidDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PurchaseBid
        fields = ['id', 'price', 'product']

    def to_internal_value(self, data):
        product = self.context['product']
        price = data['price']
        if product.size == 'ALL':
            raise serializers.ValidationError({
                'size': 'cannot bid on ALL size products'
            })
        if self.context['product'].purchase_price and price >= self.context['product'].purchase_price:
            raise serializers.ValidationError(
                {"price": "purchase bid should be less than the current purchase_price of "
                          "the product."})
        return {
            'price': price
        }


class SalesBidDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SalesBid
        fields = ['id', 'price', 'product']

    def to_internal_value(self, data):
        product = self.context['product']
        price = data['price']
        if product.size == 'ALL':
            raise serializers.ValidationError({
                'size': 'cannot bid on ALL size products'
            })
        if self.context['product'].sales_price and price <= self.context['product'].sales_price:
            raise serializers.ValidationError({"price": "sales bid should be more than the current purchase_price of "
                                                        "the product."})
        return {
            'price': price
        }


class UserPurchaseBidListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PurchaseBid
        fields = ['id', 'product', 'price', 'created_at']


class UserSalesBidListSerializer(serializers.ModelSerializer):

    class Meta:
        model = SalesBid
        fields = ['id', 'product', 'price', 'created_at']

