from django.contrib import admin
from shop.models import Product, Brand, ProductInfo, ProductImage, PurchaseBid, SalesBid, Wish

admin.site.register(Brand)
admin.site.register(ProductInfo)
admin.site.register(Product)
admin.site.register(Wish)
admin.site.register(ProductImage)
admin.site.register(PurchaseBid)
admin.site.register(SalesBid)
