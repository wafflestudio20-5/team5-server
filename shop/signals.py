from django.db.models import Min, Max
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save

from shop.models import SalesBid, TransProduct, PurchaseBid, ProductImage, StoreProduct


@receiver(post_delete, sender=ProductImage)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.image.delete(save=False)


@receiver(post_delete, sender=SalesBid)
def modify_product_price_salesbid_deleted(sender, instance, using, **kwargs):
    product = instance.product
    product.purchase_price = SalesBid.objects.filter(product=product).aggregate(price=Min('price'))['price']
    product.save()
    if product.info.transproduct_set.count()>1:
        modelproduct = TransProduct.objects.get(info=product.info, size='ALL')
        modelproduct.purchase_price = SalesBid.objects.filter(product__info=product.info).exclude(product__size='ALL').aggregate(
        price=Min('price'))['price']
        modelproduct.save()


@receiver(post_delete, sender=PurchaseBid)
def modify_product_price_purchasebid_deleted(sender, instance, using, **kwargs):
    product = instance.product
    product.sales_price = PurchaseBid.objects.filter(product=product).aggregate(price=Max('price'))['price']
    product.save()
    if product.info.transproduct_set.count() > 1:
        modelproduct = TransProduct.objects.get(info=product.info, size='ALL')
        modelproduct.sales_price = \
            PurchaseBid.objects.filter(product__info=product.info).exclude(product__size='ALL').aggregate(
                price=Max('price'))['price']
        modelproduct.save()
