from django.urls import path, include, re_path
from shop.views import WishView, BrandViewSet, TransProductRetrieveUpdateDestroyApiView, \
    StoreProductRetrieveUpdateDestroyApiView, TransProductInfoListCreateApiView, \
    StoreProductInfoListCreateApiView, StoreSizeView, TransSizeView, \
    StoreProductListCreateApiView, TransProductListCreateApiView, \
    TransProductInfoRetrieveUpdateDestroyApiView, StoreProductInfoRetrieveUpdateDestroyApiView

urlpatterns = [
    re_path(r'^transproductinfos/(?P<info>\d+)/products/(?P<size>\d+)/$', TransProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^transproductinfos/(?P<info>\d+)/products/(?P<size>\w+)/$', TransProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^storeproductinfos/(?P<info>\d+)/products/(?P<size>\w+)/$', StoreProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^storeproductinfos/(?P<info>\d+)/products/(?P<size>\w+)/$', StoreProductRetrieveUpdateDestroyApiView.as_view()),
    path('transproductinfos/<int:info>/products/', TransProductListCreateApiView.as_view()),
    path('storeproductinfos/<int:info>/products/', StoreProductListCreateApiView.as_view()),
    path('transproductinfos/<int:info>/sizes/', TransSizeView.as_view()),
    path('storeproductinfos/<int:info>/sizes/', StoreSizeView.as_view()),
    path('transproductinfos/<int:pk>/', TransProductInfoRetrieveUpdateDestroyApiView.as_view()),
    path('storeproductinfos/<int:pk>/', StoreProductInfoRetrieveUpdateDestroyApiView.as_view()),
    path('transproductinfos/', TransProductInfoListCreateApiView.as_view()),
    path('storeproductinfos/', StoreProductInfoListCreateApiView.as_view()),
    path('products/<int:pk>/wish/', WishView.as_view()),
    path('brands/', BrandViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='brand-view')
]