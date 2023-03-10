from django.urls import path, re_path

from shop.views import BrandViewSet, WishCheckView, \
    SizeWishView, ProductInfoRetrieveUpdateDestroyApiView, show_img, del_img, \
    ProductListCreateApiView, ProductRetrieveUpdateDestroyApiView, ProductInfoListCreateApiView, TransOrderCreateView, \
    StoreOrderCreateView, \
    PurchaseBidRetrieveUpdateDestroyView, SalesBidRetrieveUpdateDestroyView, BidListCreateView, OrderListView, \
    UserPurchaseBidListView, UserSalesBidListView, UserWishlistView, CommentListCreateAPIView, \
    CommentRetrieveUpdateDestroyAPIView, ReplyListCreateAPIView, ReplyRetrieveUpdateDestroyAPIView, like, \
    LikeListAPIView

urlpatterns = [
    re_path(r'^productinfos/(?P<info>\d+)/products/(?P<size>\d+)/$', ProductRetrieveUpdateDestroyApiView.as_view()),
    re_path(r'^productinfos/(?P<info>\d+)/products/(?P<size>\w+)/$', ProductRetrieveUpdateDestroyApiView.as_view()),
    path('productinfos/<int:info>/products/', ProductListCreateApiView.as_view()),
    path('productinfos/<int:info>/images/', show_img, name='image-upload'),
    path('productinfos/<int:info>/sizes/', SizeWishView.as_view()),
    path('productinfos/<int:info>/wishes/', SizeWishView.as_view()),
    path('productinfos/<int:pk>/comments/', CommentListCreateAPIView.as_view()),
    path('productinfos/<int:pk>/', ProductInfoRetrieveUpdateDestroyApiView.as_view()),
    path('productinfos/', ProductInfoListCreateApiView.as_view()),
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
    path('products/<int:pk>/transorders/', TransOrderCreateView.as_view()),
    path('products/<int:pk>/storeorders/', StoreOrderCreateView.as_view()),
    path('products/<int:pk>/bids/', BidListCreateView.as_view()),
    path('purchasebids/<int:pk>/', PurchaseBidRetrieveUpdateDestroyView.as_view()),
    path('salesbids/<int:pk>/', SalesBidRetrieveUpdateDestroyView.as_view()),
    path('orders/', OrderListView.as_view()),
    path('purchasebids/', UserPurchaseBidListView.as_view()),
    path('salesbids/', UserSalesBidListView.as_view()),
    path('wishes/', UserWishlistView.as_view()),

    path('comments/<pk>/replies/', ReplyListCreateAPIView.as_view()),
    path('<str:object_type>/<int:object_id>/like/', like, name='like/unlike'),
    path('<str:object_type>/<int:object_id>/likes/', LikeListAPIView.as_view()),
    path('comments/<pk>/', CommentRetrieveUpdateDestroyAPIView.as_view()),
    path('replies/<pk>/', ReplyRetrieveUpdateDestroyAPIView.as_view()),
]

