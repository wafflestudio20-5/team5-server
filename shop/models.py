from django.db import models
from django.dispatch import receiver
from styles.models import Post
from .utils import rename_imagefile_to_uuid
from django.contrib.auth import get_user_model

DELIVERY_CHOICES = [('immediate', 'immediate'), ('brand', 'brand')]
SHOE_SIZE_CHOICES = [('ALL', 'ALL')] + [('{0}'.format(70 + 5 * i), '{0}'.format(70 + 5 * i)) for i in range(53)]
CLOTHES_SIZE_CHOICES = [('ALL', 'ALL'), ('XXS', 'XXS'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
                        ('XXXL', 'XXXL')] + \
                       [('{0}'.format(28 + i), '{0}'.format(28 + i)) for i in range(9)]

CATECORY_CHOICES = [('shoes', 'shoes'),('clothes','clothes'),('fashion','fashion'),('life','life'),('tech','tech')]


class Brand(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class TransOrder(Order):
    buyer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='purchase_orders')
    seller = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='sales_orders')
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    # added below in case the product is deleted
    price = models.IntegerField()
    product_engname = models.CharField(max_length=100)
    size = models.CharField(choices=SHOE_SIZE_CHOICES + CLOTHES_SIZE_CHOICES, max_length=5, default='ALL')


class StoreOrder(Order):
    store = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    buyer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    price = models.IntegerField()
    product_engname = models.CharField(max_length=100)
    size = models.CharField(choices=SHOE_SIZE_CHOICES + CLOTHES_SIZE_CHOICES, max_length=5, default='ALL')


class ProductInfo(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    eng_name = models.CharField(max_length=100)
    kor_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    shares = models.ManyToManyField(through='Share', to=Post)
    delivery_tag = models.CharField(choices=DELIVERY_CHOICES, max_length=12)
    category = models.CharField(choices=CATECORY_CHOICES, max_length=10, null=True, default=None)

    class Meta:
        ordering = ['id']

class Product(models.Model):
    size = models.CharField(choices=SHOE_SIZE_CHOICES + CLOTHES_SIZE_CHOICES, max_length=5, default='ALL')
    wishes = models.ManyToManyField(through='Wish', to=get_user_model())

    class Meta:
        ordering = ['id']

class TransProduct(Product):
    purchase_price = models.IntegerField(blank=True, null=True, default=None)
    sales_price = models.IntegerField(blank=True, null=True, default=None)
    info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)

    class Meta:
        ordering = ['info']

    def __str__(self):
        return self.info.eng_name[:10]+"_"+self.size+"_"+"trans"


class StoreProduct(Product):
    sales_price = models.IntegerField()
    info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)

    class Meta:
        ordering = ['info']

    def __str__(self):
        return self.info.eng_name[:10]+"_"+self.size+"_"+"store"


# manytomanyfield
class Wish(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class Share(models.Model):
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)
    style_post = models.ForeignKey(Post, on_delete=models.CASCADE)


class ProductImage(models.Model):
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=rename_imagefile_to_uuid)


@receiver(models.signals.post_delete, sender=ProductImage)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.image.delete(save=False)


class PurchaseBid(models.Model):
    product = models.ForeignKey(TransProduct, on_delete=models.CASCADE)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.product.purchase_price is None or self.price >= self.product.purchase_price:
            self.product.purchase_price = self.price
            super(PurchaseBid, self).save(*args, **kwargs)


class SalesBid(models.Model):
    product = models.ForeignKey(TransProduct, on_delete=models.CASCADE)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.product.sales_price is None or self.price <= self.product.sales_price:
            self.product.sales_price = self.price
            super(SalesBid, self).save(*args, **kwargs)
