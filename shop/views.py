from django.http import JsonResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from shop.models import ProductInfo, Product, Wish, Brand, TransProduct, StoreProduct, TransProductInfo, \
    StoreProductInfo
from shop.permissions import IsAdminUserOrReadOnly
from shop.serializers import BrandSerializer, \
    TransProductDetailSerializer, StoreProductDetailSerializer, TransProductListSerializer, StoreProductListSerializer, \
    TransProductInfoSerializer, StoreProductInfoSerializer


# shows specific productinfo tag. superuser can update or destroy this product info.
class TransProductInfoRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = TransProductInfo.objects.all()


class StoreProductInfoRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StoreProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = StoreProductInfo.objects.all()


# shows list of productinfos.. can create new productinfo
class TransProductInfoListCreateApiView(generics.ListCreateAPIView):
    serializer_class = TransProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = TransProductInfo.objects.all()


class StoreProductInfoListCreateApiView(generics.ListCreateAPIView):
    serializer_class = StoreProductInfoSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = StoreProductInfo.objects.all()


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


class WishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        wishlist_obj, created = Wish.objects.get_or_create(product=Product.objects.get(pk=pk),
                                                           user=request.user)
        if not created:
            wishlist_obj.delete()
            return JsonResponse({"message": "WISHLIST_DELETE_SUCCESS"}, status=200)
        return JsonResponse({"message": "WISHLIST_CREATE_SUCCESS"}, status=201)


class TransSizeView(generics.ListAPIView):
    serializer_class = TransProductListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        info = self.kwargs['info']
        return TransProduct.objects.filter(info=info)


class StoreSizeView(generics.ListAPIView):
    serializer_class = StoreProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        info = self.kwargs['info']
        return StoreProduct.objects.filter(info=info)


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminUserOrReadOnly]















