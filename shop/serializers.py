from django.db.models import Count, Sum, Min
from rest_framework import serializers
import shop
from shop.models import ProductInfo, Brand, Wish, TransProduct, StoreProduct


class ProductInfoSerializer(serializers.ModelSerializer):
    productimage_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    price = serializers.SerializerMethodField()
    wishes = serializers.SerializerMethodField()
    shares = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name', 'delivery_tag', 'productimage_set', 'price','shares','wishes']

    def get_price(self, obj: ProductInfo):
        if obj.delivery_tag == 'immediate':
            return obj.transproduct_set.aggregate(price=Min('sales_price'))['price']
        return obj.storeproduct_set.aggregate(price=Min('sales_price'))['price']

    def get_wishes(self, obj: ProductInfo):
        if obj.delivery_tag == 'immediate':
            return sum(i.wish_set.count() for i in obj.transproduct_set.all())
        return sum(i.wish_set.count() for i in obj.storeproduct_set.all())

    def get_shares(self, obj:ProductInfo):
        return obj.share_set.all().count()


class TransProductListSerializer(serializers.ModelSerializer):
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES + shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = TransProduct
        fields = ['id', 'size', 'purchase_price', 'sales_price', ]
        read_only_fields = ['purchase_price', 'sales_price']

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
        fields = ['id', 'size', 'sales_price']

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
        fields = ['id', 'size', 'purchase_price', 'sales_price', 'info']

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
        fields = ['id', 'size', 'sales_price', 'info', 'size_options']

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
        fields = ['id', 'size', 'sales_price']

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
        fields = ['id', 'size', 'sales_price']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        wishcheck = False
        if Wish.objects.filter(user=user, product=instance).exists():
            wishcheck = True
        res.setdefault('user_wishcheck', wishcheck)
        return res
