from django.contrib import admin, messages
from django.http import Http404

from Cashier.models import Product, Invoice, InvoiceItem
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy

from django_plotly_dash.models import DashApp, StatelessApp
from admin_interface.models import Theme


# Register your models here.

from django.contrib import admin


admin.site.site_header = "Cashier Admin"
admin.site.site_title = "Cashier Admin Portal"
admin.site.index_title = "Welcome to Cashier Portal"


# class MyAdminSite(AdminSite):
#     def extra_style(self, *args, **kwargs):
#         return "<style></style>"


class ProductAdminProxy(Product):
    class Meta:
        proxy = True
        verbose_name = "المنتج"
        verbose_name_plural = "المنتجات"


@admin.register(ProductAdminProxy)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('ean', 'name', 'price', 'stock', 'wholesale_price')
    search_fields = ('ean', 'name')


# admin.site.register(Product, ProductAdmin)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ('get_product_name', 'quantity', 'price', 'total')
    fields = ('get_product_name', 'quantity', 'price', 'total')
    can_delete = False
    can_add_related = False
    can_change_related = False

    verbose_name = 'منتجات الفاتورة'
    verbose_name_plural = 'منتجات الفاتورة'

    def get_product_name(self, obj):
        return obj.product.name
    get_product_name.short_description = 'المنتج'

    # use model's delete method to deletion of invoice items from the invoice admin page
    def delete_model(self, request, obj):
        obj.delete()



class InvoiceAdminProxy(Invoice):
    class Meta:
        proxy = True
        verbose_name = "الفاتورة"
        verbose_name_plural = "الفواتير"


@admin.register(InvoiceAdminProxy)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'date', 'total')
    inlines = [InvoiceItemInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('invoiceitem_set')
        return queryset

    def delete_invoice_item(self, request, object_id, return_to_stock=False):
        """
        Delete an invoice item and handle quantity based on user-selected option.

        Args:
            request: Django request object.
            object_id: ID of the InvoiceItem object to be deleted.
            return_to_stock (bool, optional): True to return quantity to stock, False to mark as unsafe. Defaults to False.

        Returns:
            None

        Raises:
            Http404: If the invoice item is not found.
        """

        try:
            invoice_item = InvoiceItem.objects.get(pk=object_id)
        except InvoiceItem.DoesNotExist:
            raise Http404("Invoice item does not exist.")

        product = invoice_item.product

        # Confirm deletion with user-selected option for quantity handling.
        response = self.admin_site.action_response(
            request,
            f"حذف المنتج '{product.name}' من الفاتورة؟",
            {
                "return_to_stock": return_to_stock,
                "invoice_item_id": invoice_item.pk,
            },
        )

        if "continue" in response.POST_DATA:
            # Delete invoice item.
            invoice_item.delete()

            # Handle quantity based on user selection.
            if response.POST_DATA["return_to_stock"]:
                product.available_quantity += invoice_item.quantity
                product.save(update_fields=["available_quantity"])
            else:
                # Implement your logic for marking the quantity as unsafe here.
                # Update product or create a separate record for tracking unsafe items.
                pass

            self.message_user(request, f"تم حذف المنتج '{product.name}' بنجاح.", messages.SUCCESS)
        else:
            self.message_user(request, "تم إلغاء حذف المنتج.", messages.INFO)

        return response

# admin.site.register(Invoice, InvoiceAdmin)


