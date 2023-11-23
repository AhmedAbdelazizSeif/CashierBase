#  Copyright (c) 2023.
#

from django.urls import path

from Cashier import views
from Cashier.views import get_item_details, SoldItemsByDateView

from dashboard_app import app

urlpatterns = [
    path('', views.index, name='index'),
    path('get_item_details/<str:item_barcode>/', get_item_details, name='get_item_details'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('send_invoice/', views.send_invoice, name='send_invoice'),
    path('<str:date>/sold_items/', SoldItemsByDateView.as_view(), name='sold_items_by_date'),
    path('login/', views.login_user, name='login'),
    path('login/submit', views.login_submit, name='login_submit'),
    path('logout/', views.logout_user, name='logout'),
    # path('reactpy/', views.reactpage, name='reactpage'),
]
