from django.http import JsonResponse
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from shop.models import ProductInfo, Product, Wish
from shop.permissions import IsAdminUserOrReadOnly, IsAuthenticatedOrReadInfo
from shop.serializers import ProductDetailSerializer, ProductTagSerializer, ProductListSerializer


# shows specific productinfo tag. superuser can update or destroy this product info.
class ProductTagRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductTagSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = ProductInfo.objects.all()


# shows list of productinfos.. can create new productinfo
class ProductInfoListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductTagSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = ProductInfo.objects.all()


# shows list of products according to productinfo.. can create new product for productinfo
class ProductListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        info = self.kwargs['info']
        return Product.objects.filter(info=info).select_related('info').prefetch_related('wishes')


# shows specific product and allows superuser to update or destroy the product
class ProductRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [IsAuthenticatedOrReadInfo]
    lookup_field = 'size'

    def get_queryset(self):
        info = self.kwargs['info']
        return Product.objects.filter(info=info).select_related('info').prefetch_related('wishes')


class WishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wishlist_obj, created = Wish.objects.get_or_create(product=self.kwargs['pk'], user=request.user.id)
        if not created:
            wishlist_obj.delete()
            return JsonResponse({"message": "WISHLIST_DELETE_SUCCESS"}, status=200)
        return JsonResponse({"message": "WISHLIST_CREATE_SUCCESS"}, status=201)


class SizeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        Product.objects.filter(info=self.kwargs['pk'])







