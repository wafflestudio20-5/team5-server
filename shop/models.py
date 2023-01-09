from django.db import models
from .utils import rename_imagefile_to_uuid
from django.contrib.auth import get_user_model


class Brand(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


DELIVERY_CHOICES = [('immediate', 'immediate'), ('brand', 'brand')]
SHOE_SIZE_CHOICES = [('ALL', 'ALL')] + [('{0}'.format(70 + 5 * i), '{0}'.format(70 + 5 * i)) for i in range(53)]
CLOTHES_SIZE_CHOICES = [('ALL', 'ALL'), ('XXS', 'XXS'), ('XS', 'XS'), ('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'),
                        ('XXXL', 'XXXL')] + \
                       [('{0}'.format(28 + i), '{0}'.format(28 + i)) for i in range(9)]


class ProductInfo(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    eng_name = models.CharField(max_length=100)
    kor_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_tag = models.CharField(choices=DELIVERY_CHOICES, max_length=10)

    # shares = models.ManyToManyField(through='Share', to=)

    def __str__(self):
        return self.eng_name[:10]


class Product(models.Model):
    info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)
    size = models.CharField(choices=SHOE_SIZE_CHOICES + CLOTHES_SIZE_CHOICES, max_length=5, default='ALL')
    wishes = models.ManyToManyField(through='Wish', to=get_user_model())
<<<<<<< HEAD
    purchase_candidates = models.ManyToManyField(through='PurchaseBid', to=get_user_model())
    sales_candidates = models.ManyToManyField(through='SalesBid', to=get_user_model())
=======
>>>>>>> dbd7018c9e9ad3c9ffe2213f0eb9d4455bb94aaa
    purchase_price = models.IntegerField(blank=True, null=True, default=None)
    sales_price = models.IntegerField(blank=True, null=True, default=None)

    class Meta:
        ordering = ['info']

    def __str__(self):
        return self.info.eng_name[:10]+"_"+self.size


# manytomanyfield
class Wish(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


# manytomanyfield
# class Share(models.Model):
#     product = models.ForeignKey(ProductInfo)


class ProductImage(models.Model):
    product = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=rename_imagefile_to_uuid)


class PurchaseBid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
=======
>>>>>>> dbd7018c9e9ad3c9ffe2213f0eb9d4455bb94aaa

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.product.purchase_price is None or self.price >= self.product.purchase_price:
            self.product.purchase_price = self.price
            super(PurchaseBid, self).save(*args, **kwargs)


class SalesBid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
=======
>>>>>>> dbd7018c9e9ad3c9ffe2213f0eb9d4455bb94aaa

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.product.sales_price is None or self.price <= self.product.sales_price:
            self.product.sales_price = self.price
            super(SalesBid, self).save(*args, **kwargs)
