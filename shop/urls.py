from django.urls import path, re_path
from shop.views import BrandViewSet, WishCheckView, \
    SizeWishView, ProductInfoRetrieveUpdateDestroyApiView, show_img, del_img, \
    ProductListCreateApiView, ProductRetrieveUpdateDestroyApiView, ProductInfoListCreateApiView

urlpatterns = [
    re_path(r'^productinfos/(?P<info>\d+)/products/(?P<size>\d+)/$', ProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^productinfos/(?P<info>\d+)/products/(?P<size>\w+)/$', ProductRetrieveUpdateDestroyApiView.as_view()),
    path('productinfos/<int:info>/products/', ProductListCreateApiView.as_view()),
    path('productinfos/', ProductInfoListCreateApiView.as_view()),
    path('productinfos/<int:info>/images/', show_img, name='image-upload'),
    path('productinfos/<int:info>/sizes/', SizeWishView.as_view()),
    path('productinfos/<int:info>/wishes/', SizeWishView.as_view()),
    path('productinfos/<int:pk>/', ProductInfoRetrieveUpdateDestroyApiView.as_view()),
    path('products/<int:pk>/wishes/', WishCheckView.as_view()),
    path('productimages/<int:pk>/', del_img, name='image-delete'),
    path('brands/', BrandViewSet.as_view({
        'get': 'list',
        'post': 'create',
        }), name='brand-view'),
    path('brands/<int:pk>/', BrandViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'delete': 'destroy'
        }), name='brand-view'),
    path('products/<int:pk>/purchasebids/', PurchaseBidViewSet.as_view({
        'get': 'list',
        'post': 'create',
        }), name='brand-view'),
    path('produdcts/<int:pk>/salesbids/', SalesBidViewSet.as_view({
        'get': 'list',
        'post': 'create',
        }), name='brand-view'),
    path('purchasebids/<int:pk>/'),
    path('salesbids/<int:pk>/')
]
