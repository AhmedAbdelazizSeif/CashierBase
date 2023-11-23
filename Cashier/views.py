import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django_plotly_dash.models import DashApp, StatelessApp
from Cashier.models import Product, Invoice, InvoiceItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
import pandas as pd
from dashboard_app import app
# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    else:
        return redirect('login')


def get_item_details(request, item_barcode):
    """
    Returns the details of an item, given its barcode.
    """

    item = Product.objects.get(ean=item_barcode)

    item_details = {
        'name': item.name,
        'price': item.price,
        'ean': item.ean
    }

    return JsonResponse(item_details)


def send_invoice(request):
    if request.method == 'POST':
        # Get data from the request
        invoiceDetails = json.loads(request.POST.get('invoiceDetails'))
        # Create the invoice
        invoice = Invoice(date=datetime.now())
        invoice.save()

        # Create and associate invoice items
        for product_id, quantity in invoiceDetails.items():
            product = Product.objects.get(ean=product_id)
            price = product.price
            total = price * int(quantity)

            invoice_item = InvoiceItem(invoice=invoice, product=product, quantity=quantity, price=price, total=total)
            invoice_item.save()

        # Update the total for the invoice
        invoice.total = sum(item.total for item in invoice.invoiceitem_set.all())
        invoice.save()

        # Redirect to a success page or return a response
        return redirect('index')  # Change 'invoice_success' to the actual success page name

# Create a class based view for the send invoice page so it can handle both the invoice saving as done above and the invoice printing to pdf using ironpdf
#
# class SendInvoiceView(View):
#
#     def print_invoice(self, request):
#         if request.method == 'POST':
#             # Get data from the request
#             invoiceDetails = json.loads(request.POST.get('invoiceDetails'))
#             # Create the invoice
#             invoice = Invoice(date=datetime.now())
#             invoice.save()
#
#             # Create and associate invoice items
#             for product_id, quantity in invoiceDetails.items():
#                 product = Product.objects.get(ean=product_id)
#                 price = product.price
#                 total = price * int(quantity)
#
#                 invoice_item = InvoiceItem(invoice=invoice, product=product, quantity=quantity, price=price,
#                                            total=total)
#                 invoice_item.save()
#
#             # Update the total for the invoice
#             invoice.total = sum(item.total for item in invoice.invoiceitem_set.all())
#             invoice.save()
#
#             # Create a PDF
#             renderer = ChromePdfRenderer()
#             html = render(request, 'invoice.html', {'invoice': invoice})
#             pdf.SaveAs('invoice.pdf')
#
#             # Redirect to a success page or return a response
#             return redirect('index')


class SoldItemsByDateView(View):
    def get(self, request, date):
        # Get all invoices for the specified date.
        invoices = Invoice.objects.filter(date=date)

        # Create a list to store the sold items.
        sold_items = []

        # Iterate over the invoices and add the sold items to the list.
        for invoice in invoices:
            invoice_items = InvoiceItem.objects.filter(invoice=invoice)

            for invoice_item in invoice_items:
                sold_item = {
                    'product': Product.objects.get(ean=invoice_item.product.ean).name,
                    'quantity': invoice_item.quantity,
                    'price': invoice_item.price,
                    'total': invoice_item.total
                }

                sold_items.append(sold_item)

        # Calculate the total revenue for the sold items.
        total_revenue = 0
        for sold_item in sold_items:
            total_revenue += sold_item['total']

        # Return the sold items and total revenue to the template.
        context = {
            'sold_items': sold_items,
            'total_revenue': total_revenue
        }

        return render(request, 'testInvoice.html', context)


def dashboard(request):
    stateless = StatelessApp.objects.get(app_name='DashboardApp')
    dashapp = DashApp.objects.get(stateless_app=stateless)
    return render(request, 'dashboard.html', {'dashapp': dashapp})

def login_user(request):
    return render(request, 'login.html')


def login_submit(request):
    context = {}
    username = request.POST['user']
    password = request.POST['passwd']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('index')
    else:
        context['error_message'] = 'Invalid username or password'
        return render(request, 'login.html', context)

@login_required
def logout_user(request):
    auth_logout(request)
    return redirect('index')


#
# def reactpage(request):
#     return render(request, 'react.html')
