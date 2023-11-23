#  Copyright (c) 2023.
#

# For Firebase (using Firebase Admin SDK)
from firebase_admin import db

# For MySQL (using Django models)
from Cashier.models import Product, InvoiceItem


def get_data_from_mysql():
    return Product.objects.all()


def save_data_to_mysql(data):
    for item in data:
        item.save()




def get_data_from_firebase():
    ref = db.reference("https://cashierbasedb-default-rtdb.europe-west1.firebasedatabase.app/products")
    return ref.get()


def save_data_to_firebase(data):
    ref = db.reference("https://cashierbasedb-default-rtdb.europe-west1.firebasedatabase.app/products")
    ref.set(data)
