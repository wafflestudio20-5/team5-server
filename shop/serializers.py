from django.db.models import Count
from rest_framework import serializers
import shop
from shop.models import ProductInfo, Brand, Wish, TransProduct, StoreProduct


class ProductInfoSerializer(serializers.ModelSerializer):
    productimage_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name', 'delivery_tag', 'productimage_set']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.setdefault('brand_name', instance.brand.name)
        if instance.delivery_tag == "immediate":
            productset = instance.transproduct_set.all()
        else:
            productset = instance.storeproduct_set.all()
        try:
            res.setdefault('price', productset.order_by('sales_price')[0].sales_price)
        except:
            res.setdefault('price', None)
        try:
            res.setdefault('total_wishes', productset.aggregate(Count('wishes'))['wishes__count'])
        except:
            res.setdefault('total_wishes', 0)
        try:
            res.setdefault('total_shares', instance.share_set.all().count())
        except:
            res.setdefault('total_shares', 0)
        return res


class TransProductListSerializer(serializers.ModelSerializer):
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)

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
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)

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
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = TransProduct
        fields = ['id', 'size', 'purchase_price', 'sales_price', 'info']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_anonymous:
            wishcheck=False
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
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)
    size_options = serializers.SerializerMethodField()

    class Meta:
        model = StoreProduct
        fields = ['id', 'size', 'sales_price', 'info', 'size_options']

    def get_size_options(self, obj: StoreProduct):
        return [i.size for i in StoreProduct.objects.filter(info=obj.info) if i.size !='ALL']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        if user.is_anonymous:
            wishcheck=False
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
        wishcheck=False
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
