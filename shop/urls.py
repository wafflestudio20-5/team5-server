from django.urls import path, include, re_path
from shop.views import ProductRetrieveUpdateDestroyApiView, \
    ProductListCreateApiView, ProductInfoListCreateApiView, ProductTagRetrieveUpdateDestroyApiView, WishView, SizeView

urlpatterns = [
    re_path(r'^productinfo/(?P<info>\d+)/products/(?P<size>\d+)/$', ProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^productinfo/(?P<info>\d+)/products/(?P<size>\w+)/$', ProductRetrieveUpdateDestroyApiView.as_view()),
    path('productinfo/<int:info>/products/', ProductListCreateApiView.as_view()),
    path('productinfo/<int:pk>/', ProductTagRetrieveUpdateDestroyApiView.as_view()),
    path('productinfo/<int:pk>/sizes', SizeView.as_view()),
    path('productinfo/', ProductInfoListCreateApiView.as_view()),
    path('products/<int:pk>/wish/', WishView.as_view()),
]