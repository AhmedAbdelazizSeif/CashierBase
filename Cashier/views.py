import json
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.views import View
from django_plotly_dash.models import DashApp, StatelessApp
from Cashier.models import Product, Invoice, InvoiceItem, Customer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from Cashier.CashierFunctions.comparison_pair import comparison_pair
# Create your views her/e.

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
        invoice = Invoice(date=datetime.now(),
                          customer_id=invoiceDetails['customer'] if invoiceDetails['customer'] else None, cashier_id=request.user.id)
        invoice.save()

        # Create and associate invoice items
        for product_id, quantity in invoiceDetails['products'].items():
            product = Product.objects.get(ean=product_id)
            price = product.price
            total = price * float(quantity)

            invoice_item = InvoiceItem(invoice=invoice, product=product, quantity=quantity, price=price, total=total)
            invoice_item.save()

        # Update the total for the invoice
        invoice.total = sum(item.total for item in invoice.invoiceitem_set.all())
        invoice.save()

        # Redirect to a success page or return a response
        return redirect('index')  # Change 'invoice_success' to the actual success page name


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
            'total_revenue': total_revenue,
            'date': date
        }

        return render(request, 'testInvoice.html', context)


def dashboard(request):
    stateless = StatelessApp.objects.get(app_name='DashboardApp')
    dashapp = DashApp.objects.get(stateless_app=stateless)

    datetoday = datetime.now().date().strftime("%Y-%m-%d")
    print(datetoday)

    total_daily_sales = Invoice.objects.filter(date=datetime.now()).aggregate(total_daily_sales=Sum('total'))['total_daily_sales'] if Invoice.objects.filter(date=datetime.now()).aggregate(total_daily_sales=Sum('total'))['total_daily_sales'] else 0.00
    total_monthly_sales = Invoice.objects.filter(date__month=datetime.now().month).aggregate(total_monthly_sales=Sum('total'))['total_monthly_sales'] if Invoice.objects.filter(date__month=datetime.now().month).aggregate(total_monthly_sales=Sum('total'))['total_monthly_sales'] else 0.00
    total_weekly_sales = Invoice.objects.filter(date__week=datetime.now().isocalendar()[1]).aggregate(total_weekly_sales=Sum('total'))['total_weekly_sales'] if Invoice.objects.filter(date__week=datetime.now().isocalendar()[1]).aggregate(total_weekly_sales=Sum('total'))['total_weekly_sales'] else 0.00
    total_yearly_sales = Invoice.objects.filter(date__year=datetime.now().year).aggregate(total_yearly_sales=Sum('total'))['total_yearly_sales'] if Invoice.objects.filter(date__year=datetime.now().year).aggregate(total_yearly_sales=Sum('total'))['total_yearly_sales'] else 0.00

    last_day_sales = Invoice.objects.filter(date=datetime.strptime(datetoday,"%Y-%m-%d") - timedelta(days=1)).aggregate(last_day_sales=Sum('total'))['last_day_sales'] if Invoice.objects.filter(date=datetime.now().date() - timedelta(days=1)).aggregate(last_day_sales=Sum('total'))['last_day_sales'] else 0.00
    last_week_sales = Invoice.objects.filter(date__week=datetime.now().isocalendar()[1] - 1).aggregate(last_week_sales=Sum('total'))['last_week_sales'] if Invoice.objects.filter(date__week=datetime.now().isocalendar()[1] - 1).aggregate(last_week_sales=Sum('total'))['last_week_sales'] else 0.00
    last_month_sales = Invoice.objects.filter(date__month=datetime.now().month - 1).aggregate(last_month_sales=Sum('total'))['last_month_sales'] if Invoice.objects.filter(date__month=datetime.now().month - 1).aggregate(last_month_sales=Sum('total'))['last_month_sales'] else 0.00
    last_year_sales = Invoice.objects.filter(date__year=datetime.now().year - 1).aggregate(last_year_sales=Sum('total'))['last_year_sales'] if Invoice.objects.filter(date__year=datetime.now().year - 1).aggregate(last_year_sales=Sum('total'))['last_year_sales'] else 0.00

    context = {
        'total_daily_sales': total_daily_sales,
        'total_weekly_sales': total_weekly_sales,
        'total_monthly_sales': total_monthly_sales,
        'total_yearly_sales': total_yearly_sales,
        'diff_daily_percentage': comparison_pair(total_daily_sales, last_day_sales),
        'diff_weekly_percentage': comparison_pair(total_weekly_sales, last_week_sales),
        'diff_monthly_percentage': comparison_pair(total_monthly_sales, last_month_sales),
        'diff_yearly_percentage': comparison_pair(total_yearly_sales, last_year_sales),
        'dashapp': dashapp,
        'date': datetoday
    }
    return render(request, 'dashboard.html', context)

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


def get_customer_details(request, phone):
    """
    Returns the details of the first customer whose phone number matches the pattern.
    """

    pattern = f"^({phone})"  # Build the regex pattern.
    query = Q(phone__regex=pattern)

    customer = Customer.objects.filter(query).first()

    if customer:
        customer_details = {
            'id': customer.id,
            'first_name': customer.name.split()[0],
            'last_name': customer.name.split()[1],
            'phone2': customer.phone2,
            'address': customer.address,
            'change': customer.change,
            'debt': customer.debt
        }
        return JsonResponse(customer_details)
    else:
        return HttpResponseNotFound()


def new_customer(request):
    if request.method == 'POST':
        # Get data from the request
        customerDetails = {
            'name': " ".join([request.POST.get('first_name'), request.POST.get('last_name')]),
            'phone': request.POST.get('phone'),
            'phone2': request.POST.get('phone2'),
            'address': request.POST.get('address'),
            'change': request.POST.get('change') if request.POST.get('change') else 0,
            'debt': request.POST.get('debt') if request.POST.get('debt') else 0
        }
        # Create the customer
        customer = Customer(**customerDetails)
        customer.save()

        # Redirect to a success page or return a response
        return JsonResponse({'customer_id': customer.id})


def invoices(request):
    invoices = Invoice.objects.filter(archived=False).order_by('-date')
    page_obj = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    context = {
        'invoices': page_obj.get_page(page_number),
        'page_obj': page_obj,
    }
    return render(request, 'invoices.html', context)


def invoice_details(request, invoice_custom_id):
    invoice = Invoice.objects.get(custom_id=invoice_custom_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'user': request.user
    }
    return render(request, 'invoice_details.html', context)


def archive_invoices(request):
    if request.method == 'POST':
        selected_invoices = request.POST.getlist('selected-invoices')
        for invoice_id in selected_invoices:
            Invoice.objects.filter(custom_id=invoice_id).update(archived=True)
        # Redirect to the invoices view
        return redirect('invoices')


def archived_invoices(request):
    invoices = Invoice.objects.filter(archived=True).order_by('-date')
    page_obj = Paginator(invoices, 10)
    page_number = request.GET.get('page')
    context = {
        'invoices': page_obj.get_page(page_number),
        'page_obj': page_obj,
    }
    return render(request, 'archived_invoices.html', context)


def archived_invoice_details(request, invoice_custom_id):
    invoice = Invoice.objects.get(custom_id=invoice_custom_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'user': request.user
    }
    return render(request, 'archived_invoice_details.html', context)


def unarchive_invoices(request, invoice_custom_id):
    if request.method == 'POST':
        selected_invoices = request.POST.getlist('selected-invoices')
        for invoice_id in selected_invoices:
            Invoice.objects.filter(custom_id=invoice_id).update(archived=False)
        # Redirect to the invoices view
        return redirect('archived_invoices')