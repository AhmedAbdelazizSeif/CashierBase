#  Copyright (c) 2023.
#

from django.urls import path

from Cashier import views
from Cashier.views import get_item_details, SoldItemsByDateView

from dashboard_app import app


urlpatterns = [
    path('', views.index, name='index'),
    path('get_item_details/<str:item_barcode>/', get_item_details, name='get_item_details'),
    path('get_customer_details/<str:phone>/', views.get_customer_details, name='get_customer_details'),
    path('new_customer/', views.new_customer, name='new_customer'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/invoices/', views.invoices, name='invoices'),
    path('dashboard/invoices/<str:invoice_custom_id>/', views.invoice_details, name='invoice_details'),
    path('archive_invoices/', views.archive_invoices, name='archive_invoices'),
    path('archive_invoices/<str:invoice_custom_id>/', views.archived_invoice_details, name='archive_invoice_details'),
    path('archived_invoices/', views.archived_invoices, name='archived_invoices'),
    path('unarchive_invoice/<str:invoice_custom_id>/', views.unarchive_invoices, name='unarchive_invoice'),
    path('send_invoice/', views.send_invoice, name='send_invoice'),
    path('<str:date>/sold_items/', SoldItemsByDateView.as_view(), name='sold_items_by_date'),
    path('login/', views.login_user, name='login'),
    path('login/submit', views.login_submit, name='login_submit'),
    path('logout/', views.logout_user, name='logout'),
    # path('reactpy/', views.reactpage, name='reactpage'),
]
