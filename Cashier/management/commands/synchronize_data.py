# #  Copyright (c) 2023.
# #
#
# # In your Django app's management/commands/synchronize_data.py
#
# from django.core.management.base import BaseCommand
# import time
# import threading
# from Cashier.data_sync import get_data_from_mysql, save_data_to_mysql, get_data_from_firebase, save_data_to_firebase
#
# class Command(BaseCommand):
#     help = 'Synchronize data between MySQL and Firebase'
#
#     def handle(self, *args, **options):
#         while True:
#             mysql_data = get_data_from_mysql()
#             save_data_to_firebase(mysql_data)
#
#             firebase_data = get_data_from_firebase()
#             save_data_to_mysql(firebase_data)
#
#             time.sleep(60) # Run every 60 seconds
#
