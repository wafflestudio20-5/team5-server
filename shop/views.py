from rest_framework import generics
from rest_framework.permissions import AllowAny
from shop.models import ProductInfo, Product
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









