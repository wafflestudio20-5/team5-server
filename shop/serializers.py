from django.contrib.contenttypes.models import ContentType
from django.db.models import Min
from rest_framework import serializers
import shop
from accounts.models import CustomUser
from shop.models import ProductInfo, Brand, Wish, TransProduct, StoreProduct, TransOrder, StoreOrder, PurchaseBid, \
    SalesBid, Order, Reply, Like, Comment
from styles.models import Profile
from styles.serializers import NestedProfileSerializer


class ProductInfoSerializer(serializers.ModelSerializer):
    productimage_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    productimage_urls = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    wishes = serializers.SerializerMethodField()
    shares = serializers.SerializerMethodField()

    class Meta:
        model = ProductInfo
        fields = ['id', 'brand', 'eng_name', 'kor_name', 'delivery_tag', 'productimage_set', 'price', 'shares',
                  'wishes', 'brand_name', 'productimage_urls']

    def get_productimage_urls(self, obj: ProductInfo):
        return [pd_image.image.url for pd_image in obj.productimage_set.all()]

    def get_brand_name(self, obj: ProductInfo):
        return obj.brand.name

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
        fields = ['id', 'size', 'purchase_price', 'sales_price']

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
        if product.size == 'ALL' and product.info.transproduct_set.count()>1:
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
        if product.size == 'ALL' and product.info.transproduct_set.count()>1:
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
        if product.size == 'ALL' and product.info.transproduct_set.count()>1:
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
        if product.size == 'ALL' and product.info.transproduct_set.count()>1:
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


class UserWishlistSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        product = instance.product
        try:
            info = product.transproduct.info
            size = instance.product.transproduct.size
            price = instance.product.transproduct.purchase_price
        except:
            info = product.storeproduct.info
            size = instance.product.storeproduct.size
            price = instance.product.storeproduct.purchase_price
        return {
            'product_id': product.id,
            'brand_name': info.brand.name,
            'eng_name': info.eng_name,
            'size': size,
            'price': price,
            'created_at': instance.created_at
        }


class InfoReplySerializer(serializers.ModelSerializer):
    to_profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())
    created_by = NestedProfileSerializer(read_only=True)
    num_likes = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = ['id', 'content', 'to_profile', 'created_by', 'created_at', 'num_likes']
        read_only_fields = ['id', 'created_by', 'created_at', 'num_likes']

    def get_num_likes(self, obj: Reply):
        return obj.likes.count()

    def to_representation(self, instance: Reply):
        representation = super().to_representation(instance)
        representation = {
            **representation,
            'to_profile': {
                'user_id': instance.to_profile.user_id,
                'profile_name': instance.to_profile.profile_name
            }
        }
        current_user: CustomUser = self.context['request'].user
        if current_user.is_anonymous:
            return {**representation, 'liked': 'login required'}

        liked = Like.objects.filter(from_profile_id=current_user.id,
                                    content_type=ContentType.objects.get_for_model(instance),
                                    object_id=instance.id).exists()
        return {**representation, 'liked': liked}

    def create(self, validated_data):
        current_user: CustomUser = self.context['request'].user
        comment_id = self.context['comment_id']
        info_id = Comment.objects.get(id=comment_id).info_id
        instance = Reply.objects.create(**validated_data, info_id=info_id, comment_id=comment_id,
                                        created_by_id=current_user.id)
        return instance


class InfoCommentListSerializer(serializers.ModelSerializer):
    created_by = NestedProfileSerializer(read_only=True)
    replies = InfoReplySerializer(many=True, read_only=True)
    num_likes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'created_at', 'replies', 'num_likes']
        read_only_fields = ['id', 'created_by', 'created_at', 'replies', 'num_likes']

    def get_num_likes(self, obj: Comment):
        return obj.likes.count()

    def to_representation(self, instance: Comment):
        representation = super().to_representation(instance)
        current_user: CustomUser = self.context['request'].user
        if current_user.is_anonymous:
            return {**representation, 'liked': 'login required'}

        liked = Like.objects.filter(from_profile_id=current_user.id,
                                    content_type=ContentType.objects.get_for_model(instance),
                                    object_id=instance.id).exists()
        return {**representation, 'liked': liked}

    def create(self, validated_data):
        current_user: CustomUser = self.context['request'].user
        instance = Comment.objects.create(**validated_data, info_id=self.context['info_id'],
                                          created_by_id=current_user.id)
        return instance


class InfoCommentDetailSerializer(serializers.ModelSerializer):
    created_by = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'created_by', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class InfoLikeListSerializer(serializers.ModelSerializer):
    from_profile = NestedProfileSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['from_profile', 'created_at']
        read_only_fields = ['from_profile', 'created_at']


