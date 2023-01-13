from django.http import JsonResponse
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import  IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from shop.models import ProductInfo, Product, Wish, Brand, TransProduct, StoreProduct, ProductImage
from shop.permissions import IsAdminUserOrReadOnly
from shop.serializers import BrandSerializer, \
    TransProductDetailSerializer, StoreProductDetailSerializer, TransProductListSerializer, StoreProductListSerializer, \
    TransSizeWishSerializer, StoreSizeWishSerializer, ProductInfoSerializer

# shows specific productinfo tag. superuser can update or destroy this product info.
from shop.utils import rename_imagefile_to_uuid
from styles.models import PostImage


class ProductInfoRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = ProductInfo.objects.all()


# shows list of productinfos.. can create new productinfo
class ProductInfoListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = ProductInfo.objects.all()


# shows list of products according to productinfo.. can create new product for productinfo
class TransProductListCreateApiView(generics.ListCreateAPIView):
    serializer_class = TransProductListSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        info = self.kwargs['info']
        return TransProduct.objects.filter(info=info).select_related('info')


class StoreProductListCreateApiView(generics.ListCreateAPIView):
    serializer_class = StoreProductListSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        info = self.kwargs['info']
        return StoreProduct.objects.filter(info=info).select_related('info')


# shows specific product and allows superuser to update or destroy the product
class TransProductRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransProductDetailSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'size'

    def get_queryset(self):
        info = self.kwargs['info']
        return TransProduct.objects.filter(info=info).select_related('info').prefetch_related('wishes')


class StoreProductRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoreProductDetailSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'size'

    def get_queryset(self):
        info = self.kwargs['info']
        return StoreProduct.objects.filter(info=info).select_related('info').prefetch_related('wishes')


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

    def get_queryset(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransProduct.objects.filter(info=self.kwargs['info'])
        elif productinfo.delivery_tag == 'brand':
            return StoreProduct.objects.filter(info=self.kwargs['info'])

    def get_serializer_class(self):
        productinfo = get_object_or_404(ProductInfo, pk=self.kwargs['info'])
        if productinfo.delivery_tag == 'immediate':
            return TransSizeWishSerializer
        return StoreSizeWishSerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUserOrReadOnly]


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
            'message': 'OK'
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
        'message': 'OK'
    }, status=200)
