import re

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.http import JsonResponse
from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from config.exceptions import InvalidObjectTypeException
from shop.models import ProductInfo, Product, Wish, Brand, TransProduct, StoreProduct, ProductImage, PurchaseBid, \
    SalesBid, TransOrder, Order, StoreOrder, Comment, Reply, Like
from shop.paginations import CustomPagination, CommonCursorPagination
from shop.permissions import IsAdminUserOrReadOnly, IsOwner, IsWriterOrReadOnly
from shop.serializers import BrandSerializer, \
    TransProductDetailSerializer, StoreProductDetailSerializer, TransProductListSerializer, StoreProductListSerializer, \
    TransSizeWishSerializer, StoreSizeWishSerializer, ProductInfoSerializer, \
    StoreOrderDetailSerializer, TransOrderDetailSerializer, \
    PurchaseBidListSerializer, SalesBidListSerializer, PurchaseBidDetailSerializer, \
    SalesBidDetailSerializer, OrderListSerializer, UserSalesBidListSerializer, UserPurchaseBidListSerializer, \
    UserWishlistSerializer, InfoCommentListSerializer, InfoCommentDetailSerializer, InfoReplySerializer, \
    InfoLikeListSerializer
from django.db.models import Q, Prefetch, Count

# shows specific productinfo tag. superuser can update or destroy this product info.
from styles.models import Profile


class ProductInfoRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = ProductInfo.objects.all()


class ProductInfoListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = ProductInfo.objects.all()
        deltag = self.request.query_params.get('delivery_tag')
        brand_id = self.request.query_params.getlist('brand_id')
        category = self.request.query_params.getlist('category')
        price = self.request.query_params.getlist('price')
        final_condition = Q()

        if deltag:
            queryset = queryset.filter(delivery_tag=deltag)
        if brand_id:
            condition = Q()
            for id in brand_id:
                condition |= Q(brand__exact=id)
            final_condition &= condition
        if category:
            condition = Q()
            for c in category:
                condition |= Q(category__exact=c)
            final_condition &= condition
        if price:
            pattern = re.compile(r"^\d*-\d*$")
            price_condition = Q()
            for p in price:
                if not pattern.match(p):
                    raise ValidationError('price format is wrong')
                p = p.split('-')
                if not deltag or deltag == 'immediate':
                    condition = Q()
                    condition &= Q(transproduct__size='ALL', transproduct__purchase_price__gte=p[0]) if p[0] != '' else condition
                    condition &= Q(transproduct__size='ALL', transproduct__purchase_price__lte=p[1]) if p[1] != '' else condition
                    price_condition |= condition
                if not deltag or deltag == 'brand':
                    condition = Q()
                    condition &= Q(storeproduct__purchase_price__gte=p[0]) if p[0] != '' else condition
                    condition &= Q(storeproduct__purchase_price__lte=p[1]) if p[1] != '' else condition
                    price_condition |= condition
            final_condition &= price_condition
        return queryset.filter(final_condition).distinct().prefetch_related(
            'productimage_set', 'brand', 'share_set',
            Prefetch('transproduct_set',
                     queryset=TransProduct.objects.select_related('product_ptr').prefetch_related('wish_set')
                     ),
            Prefetch('storeproduct_set',
                     queryset=StoreProduct.objects.select_related('product_ptr').prefetch_related('wish_set'))
        )


# shows list of products according to productinfo.. can create new product for productinfo
class ProductListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransProduct.objects.filter(info=self.kwargs['info'])
        elif productinfo.delivery_tag == 'brand':
            return StoreProduct.objects.filter(info=self.kwargs['info'])

    def get_serializer_class(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransProductListSerializer
        return StoreProductListSerializer


# shows specific product and allows superuser to update or destroy the product
class ProductRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'size'

    def get_queryset(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransProduct.objects.filter(info=self.kwargs['info']).select_related('info')
        elif productinfo.delivery_tag == 'brand':
            return StoreProduct.objects.filter(info=self.kwargs['info']).select_related('info')

    def get_serializer_class(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransProductDetailSerializer
        return StoreProductDetailSerializer


class WishCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        wishlist_obj, created = Wish.objects.get_or_create(product=Product.objects.get(pk=pk),
                                                           user=request.user)
        if not created:
            wishlist_obj.delete()
            return JsonResponse({"message": "WISHLIST_DELETE_SUCCESS"}, status=200)
        return JsonResponse({"message": "WISHLIST_CREATE_SUCCESS"}, status=201)


class SizeWishView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransProduct.objects.filter(info=self.kwargs['info'])
        elif productinfo.delivery_tag == 'brand':
            return StoreProduct.objects.filter(info=self.kwargs['info'])
        raise FieldError

    def get_serializer_class(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransSizeWishSerializer
        return StoreSizeWishSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    pagination_class = CustomPagination


@api_view(['POST', 'GET'])
@permission_classes((IsAdminUserOrReadOnly,))
def show_img(request, info):
    if request.method == 'POST':
        try:
            img = request.FILES['product_image']
        except:
            raise ValidationError('No image has been uploaded')
        ProductImage.objects.create(product=get_object_or_404(ProductInfo, pk=info), image=img)
        return JsonResponse({
            'message': 'Created'
        }, status=201)
    else:
        return JsonResponse({
            'images': [{"id": i.pk, "url": i.image.url} for i in ProductImage.objects.filter(product=info)]
        }, status=200)


@api_view(['DELETE'])
@permission_classes((IsAdminUser,))
def del_img(request, pk):
    productimage = get_object_or_404(ProductImage, pk=pk)
    productimage.delete()
    return JsonResponse({
        'message': 'Deleted'
    }, status=204)


class TransOrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = TransOrderDetailSerializer

    # type=purchase,sales
    def get_serializer_context(self):
        context = super().get_serializer_context()
        product = get_object_or_404(TransProduct, pk=self.kwargs['pk'])
        transaction_type = self.request.query_params.get('type')
        context.update({"transaction_type": transaction_type})
        if transaction_type == 'purchase':
            try:  # choose cheapest bid
                bid = SalesBid.objects.filter(product=product)[0]
            except:
                raise ValidationError('no sales bid for purchase')
        elif transaction_type == 'sales':
            try:  # choose the most expensive bid
                bid = PurchaseBid.objects.filter(product=product)[0]
            except:
                raise ValidationError('no purchase bid for sale')
        else:
            raise ValidationError('no such transaction_type')
        context.update({"bid": bid})
        context.update({"product": product})
        context.update({"user": self.request.user})
        return context


class StoreOrderCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = StoreOrderDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product = get_object_or_404(StoreProduct, pk=self.kwargs['pk'])
        context.update({"product": product})
        context.update({"user": self.request.user})
        return context


# type purchase, sales
class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = OrderListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        type = self.request.query_params.get('type')
        user = self.request.user
        if type == 'purchase':
            transproducts = TransOrder.objects.filter(buyer=user).values_list('product').distinct()
            storeproducts = StoreOrder.objects.filter(buyer=user).values_list('product').distinct()
            return Order.objects.filter(product_id__in=list(transproducts) + list(storeproducts)).order_by(
                '-created_at')
        elif type == 'sales':
            return Order.objects.filter(
                product_id__in=TransOrder.objects.filter(seller=user).values_list(
                    'product').distinct())
        else:
            raise ValidationError('no such type')


class BidListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.query_params.get('type') == 'purchase':
            return PurchaseBidListSerializer
        elif self.request.query_params.get('type') == 'sales':
            return SalesBidListSerializer
        else:
            raise ValidationError('no such type')

    def get_queryset(self):
        product = get_object_or_404(TransProduct, pk=self.kwargs['pk'])
        if self.request.query_params.get('type') == 'purchase':
            return PurchaseBid.objects.filter(product=product).values('price').annotate(
                count=Count('price')).order_by('-price')
        elif self.request.query_params.get('type') == 'sales':
            return SalesBid.objects.filter(product=product).values('price').annotate(
                count=Count('price')).order_by('price')
        else:
            raise ValidationError('no such type for bidding')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product = get_object_or_404(TransProduct, pk=self.kwargs['pk'])
        context.update({"product": product})
        context.update({"user": self.request.user})
        return context


class UserPurchaseBidListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = UserPurchaseBidListSerializer

    def get_queryset(self):
        user = self.request.user
        return PurchaseBid.objects.filter(user=user).order_by('-created_at')


class UserSalesBidListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = UserSalesBidListSerializer

    def get_queryset(self):
        user = self.request.user
        return SalesBid.objects.filter(user=user).order_by('-created_at')


class PurchaseBidRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseBid.objects.all()
    serializer_class = PurchaseBidDetailSerializer
    permission_classes = [IsOwner, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        bid = get_object_or_404(PurchaseBid, pk=self.kwargs['pk'])
        context.update({"product": bid.product})
        return context


class SalesBidRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesBid.objects.all()
    serializer_class = SalesBidDetailSerializer
    permission_classes = [IsOwner, ]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        bid = get_object_or_404(SalesBid, pk=self.kwargs['pk'])
        context.update({"product": bid.product})
        return context


class UserWishlistView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserWishlistSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Wish.objects.filter(user_id=self.request.user).select_related('user', 'product').order_by('-created_at')


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InfoCommentListSerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(ProductInfo, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Comment.objects.select_related('created_by').prefetch_related('replies').filter(
            info_id__exact=self.kwargs.get('pk'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['info_id'] = self.kwargs.get('pk')
        return context


class CommentRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('created_by').prefetch_related('replies').all()
    serializer_class = InfoCommentDetailSerializer
    permission_classes = [IsAuthenticated & IsWriterOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ReplyListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = InfoReplySerializer
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Comment, pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Reply.objects.select_related('created_by').filter(
            comment_id__exact=self.kwargs.get('pk'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['comment_id'] = self.kwargs.get('pk')
        return context


class ReplyRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reply.objects.select_related('created_by').all()
    serializer_class = InfoReplySerializer
    permission_classes = [IsAuthenticated & IsWriterOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def like(request, **kwargs):
    if kwargs['object_type'] == 'comments':
        obj = get_object_or_404(Comment, id=kwargs['object_id'])
    elif kwargs['object_type'] == 'replies':
        obj = get_object_or_404(Reply, id=kwargs['object_id'])
    else:
        raise InvalidObjectTypeException()

    profile = Profile.objects.get(user=request.user)
    try:
        like_instance = Like.objects.get(from_profile=profile, content_type=ContentType.objects.get_for_model(obj),
                                         object_id=obj.id)
        like_instance.delete()
        return JsonResponse({'message': 'unliked successfully'}, status=status.HTTP_200_OK)

    except Like.DoesNotExist:
        Like.objects.create(from_profile=profile, content_type=ContentType.objects.get_for_model(obj), object_id=obj.id)
        return JsonResponse({'message': 'liked successfully'}, status=status.HTTP_200_OK)


class LikeListAPIView(generics.ListAPIView):
    serializer_class = InfoLikeListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommonCursorPagination

    def get_queryset(self):
        if self.kwargs['object_type'] == 'comments':
            obj = get_object_or_404(Comment, id=self.kwargs['object_id'])
        elif self.kwargs['object_type'] == 'replies':
            obj = get_object_or_404(Reply, id=self.kwargs['object_id'])
        else:
            raise InvalidObjectTypeException()

        return obj.likes
