from django.urls import path, re_path
from shop.views import BrandViewSet, TransProductRetrieveUpdateDestroyApiView, \
    StoreProductRetrieveUpdateDestroyApiView, StoreProductListCreateApiView, TransProductListCreateApiView, \
    WishCheckView, \
    SizeWishView, ProductInfoListCreateApiView, ProductInfoRetrieveUpdateDestroyApiView, show_img, del_img

urlpatterns = [
    re_path(r'^productinfos/(?P<info>\d+)/transproducts/(?P<size>\d+)/$', TransProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^productinfos/(?P<info>\d+)/transproducts/(?P<size>\w+)/$', TransProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^productinfos/(?P<info>\d+)/storeproducts/(?P<size>\w+)/$', StoreProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^productinfos/(?P<info>\d+)/storeproducts/(?P<size>\w+)/$', StoreProductRetrieveUpdateDestroyApiView.as_view()),
    path('productinfos/<int:info>/transproducts/', TransProductListCreateApiView.as_view()),
    path('productinfos/<int:info>/storeproducts/', StoreProductListCreateApiView.as_view()),
    path('productinfos/<int:pk>/', ProductInfoRetrieveUpdateDestroyApiView.as_view()),
    path('productinfos/', ProductInfoListCreateApiView.as_view()),
    path('productinfos/<int:info>/images/', show_img, name='image-upload'),
    path('productimages/<int:pk>/', del_img, name='image-delete'),
    path('productinfos/<int:info>/sizes/', SizeWishView.as_view()),
    path('productinfos/<int:info>/wishes/', SizeWishView.as_view()),
    path('products/<int:pk>/wishes/', WishCheckView.as_view()),
    path('brands/', BrandViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='brand-view'),
]