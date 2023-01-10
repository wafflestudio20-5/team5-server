from django.contrib import admin
from shop.models import Product, Brand, ProductInfo, ProductImage, PurchaseBid, SalesBid, Wish, Store, TransOrder, \
    StoreOrder

admin.site.register(Brand)
admin.site.register(Store)
admin.site.register(ProductInfo)
admin.site.register(Product)
admin.site.register(Wish)
admin.site.register(ProductImage)
admin.site.register(PurchaseBid)
admin.site.register(SalesBid)
admin.site.register(TransOrder)
admin.site.register(StoreOrder)
