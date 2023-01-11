from django.db.models import Count
from rest_framework import serializers
import shop
from shop.models import ProductInfo, Product, Brand, Wish, TransProduct, StoreProduct, TransProductInfo, \
    StoreProductInfo


class TransProductInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.setdefault('brand_name', instance.brand.name)
        try:
            res.setdefault('price', instance.transproduct_set.all().order_by('sales_price')[0].sales_price)
        except:
            res.setdefault('price', None)
        try:
            res.setdefault('total_wishes', instance.transproduct_set.all().aggregate(Count('wishes'))['wishes__count'])
        except:
            res.setdefault('total_wishes', 0)
        try:
            res.setdefault('total_shares', instance.share_set.all().count())
        except:
            res.setdefault('total_shares', 0)
        return res


class StoreProductInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = StoreProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.setdefault('brand_name', instance.brand.name)
        try:
            res.setdefault('price', instance.storeproduct_set.all().order_by('sales_price')[0].sales_price)
        except:
            res.setdefault('price', None)
        try:
            res.setdefault('total_wishes', instance.storeproduct_set.all().aggregate(Count('wishes'))['wishes__count'])
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

    def validate_size(self, size):
        if TransProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size

    def create(self, validated_data):
        validated_data['info'] = TransProductInfo.objects.get(id=self.context['view'].kwargs['info'])
        instance = super().create(validated_data)
        return instance


class StoreProductListSerializer(serializers.ModelSerializer):
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = StoreProduct
        fields = ['id', 'size', 'price']

    def validate_size(self, size):
        if StoreProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size

    def create(self, validated_data):
        validated_data['info'] = StoreProductInfo.objects.get(id=self.context['view'].kwargs['info'])
        instance = super().create(validated_data)
        return instance


class TransProductDetailSerializer(serializers.ModelSerializer):
    info = TransProductInfoSerializer(read_only=True)
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = TransProduct
        fields = ['id', 'size', 'purchase_price', 'sales_price', 'info']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        wishcheck=True
        if user.is_anonymous:
            wishcheck=False
        elif not Wish.objects.filter(user=user, product=instance).exists():
            wishcheck=False
        res.setdefault('user_wishcheck', wishcheck)
        return res

    def validate_size(self, size):
        if TransProduct.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size


class StoreProductDetailSerializer(serializers.ModelSerializer):
    info = StoreProductInfoSerializer(read_only=True)
    size = serializers.ChoiceField(choices=shop.models.SHOE_SIZE_CHOICES+shop.models.CLOTHES_SIZE_CHOICES)

    class Meta:
        model = StoreProduct
        fields = ['id', 'size', 'price', 'info']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        user = self.context['request'].user
        wishcheck=True
        if user.is_anonymous:
            wishcheck=False
        elif not Wish.objects.filter(user=user, product=instance).exists():
            wishcheck=False
        res.setdefault('user_wishcheck', wishcheck)
        return res

    def validate_size(self, size):
        if Product.objects.filter(info=self.context['view'].kwargs['info'], size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name']

