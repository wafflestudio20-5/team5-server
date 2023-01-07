import json
from django.db.models import Count
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from shop.models import ProductInfo, Product


class ProductTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name', 'delivery_tag']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.setdefault('brand_name', instance.brand.name)
        res.setdefault('price', instance.product_set.order_by('sales_price')[0].sales_price)
        res.setdefault('total_wishes', instance.product_set.aggregate(Count('wishes'))['wishes__count'])
        return res


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'size', 'purchase_price', 'sales_price', 'wishes', 'info']

    def validate_size(self, size):
        if Product.objects.filter(info=self.initial_data.get('info'), size=size).exists() > 0:
            raise serializers.ValidationError({"size": "This size already exists"})
        return size


class ProductDetailSerializer(serializers.ModelSerializer):
    info = ProductTagSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'size', 'purchase_price', 'sales_price', 'wishes', 'info']

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res.setdefault('sizes', [i.size for i in Product.objects.filter(info=instance.info)])
        return res

    def validate_size(self, size):
        if Product.objects.filter(info=self.instance.info.id, size=size).exists():
            raise serializers.ValidationError({"size": "This size already exists"})
        return size


