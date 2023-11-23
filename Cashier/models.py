from datetime import datetime
from django.db import models
from django.db.models.signals import post_save
from django.db.models import F
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.
class Product(models.Model):
    ean = models.CharField(primary_key=True, max_length=13)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.IntegerField()
    wholesale_price = models.FloatField()
    # price_per_pack = models.FloatField()
    # small_packets_per_big_pack = models.IntegerField()
    def __str__(self):
        return self.name


class Customer(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, null=True)


class Invoice(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=timezone.now)
    total = models.FloatField(null=True)
    items = models.ManyToManyField(Product, through='InvoiceItem')


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    price = models.FloatField()
    total = models.FloatField()

@receiver(post_save, sender=InvoiceItem)
def update_stock(sender, instance, **kwargs):
    ean = instance.product
    product = instance.product
    product.stock -= int(instance.quantity)
    product.save()


class Seller(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100, null=False)
    company = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, null=True)


class WholesaleInvoice(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True)
    date = models.DateField(default=timezone.now)
    total = models.FloatField()
    items = models.ManyToManyField(Product, through='WholesaleInvoiceItem')


class WholesaleInvoiceItem(models.Model):
    invoice = models.ForeignKey(WholesaleInvoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    price_per_pack = models.FloatField()
    small_packets_per_big_pack = models.IntegerField()

    @property
    def price(self):
        return self.price_per_pack / self.small_packets_per_big_pack


@receiver(post_save, sender=WholesaleInvoiceItem)
def update_stock(sender, instance, **kwargs):
    product = instance.product
    product.stock += sender.quantity
    product.wholesale_price = sender.price
    product.save()


post_save.connect(update_stock, sender=WholesaleInvoiceItem)
