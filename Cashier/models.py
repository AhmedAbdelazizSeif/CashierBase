from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Max
from django.contrib.auth.models import User


# Create your models here.
class Product(models.Model):
    ean = models.CharField(primary_key=True, max_length=13)
    name = models.CharField(max_length=100)
    price = models.FloatField()
    stock = models.FloatField(default=0.0)
    wholesale_price = models.FloatField()

    # price_per_pack = models.FloatField()
    # small_packets_per_big_pack = models.IntegerField()
    def __str__(self):
        return self.name


class AbstractCustomerSeller(models.Model):
    """
    Abstract base class for Customer and Seller models.
    """
    name = models.CharField(max_length=100, null=False)
    phone = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, null=True)
    change = models.FloatField(default=0)
    debt = models.FloatField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Customer(AbstractCustomerSeller):
    address = models.CharField(max_length=100, null=False)


class Seller(AbstractCustomerSeller):
    company = models.CharField(max_length=100, null=False)




class Invoice(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    custom_id = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    total = models.FloatField(null=True)
    items = models.ManyToManyField(Product, through='InvoiceItem', )
    archived = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.custom_id:
            # Generate the next ID based on the current date and max ID
            max_id = Invoice.objects.filter(date=self.date).aggregate(max_id=Max('custom_id'))['max_id']
            next_id = 1 if max_id is None else int(max_id[-2:]) + 1
            date_str = self.date.strftime('%Y%m%d')
            self.custom_id = f"{date_str}{next_id:06d}"

        super(Invoice, self).save(*args, **kwargs)

    def __str__(self):
        return self.custom_id


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()
    price = models.FloatField()
    total = models.FloatField()

    # Method to allow the admin to delete items from the invoice
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.invoice.total -= self.total
        self.invoice.save()


@receiver(post_save, sender=InvoiceItem)
def update_stock(sender, instance, **kwargs):
    ean = instance.product
    product = instance.product
    product.stock -= float(instance.quantity)
    product.save()


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
