from django.contrib import admin
from Cashier.models import Product, Invoice, InvoiceItem
from django_plotly_dash.models import DashApp, StatelessApp


# Register your models here.


class ProductAdmin():
    list_display = ('ean', 'name', 'price', 'stock', 'wholesale_price')
    search_fields = ('ean', 'name')
    list_filter = ('price', 'stock', 'wholesale_price')
    ordering = ('name', 'price', 'stock', 'wholesale_price')
    readonly_fields = ('ean', 'name')


admin.site.register(Product)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ('get_product_name', 'quantity', 'price', 'total')
    can_delete = False
    can_add_related = False
    can_change_related = False

    def get_product_name(self, obj):
        return obj.product.name

    get_product_name.short_description = 'Product'

    def get_verbose_name(self, field_name):
        if field_name == 'product':
            return 'Product Name'

        return field_name.replace('_', ' ').capitalize()


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'total')
    inlines = [InvoiceItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('invoiceitem_set')
        return queryset


admin.site.register(Invoice, InvoiceAdmin)
