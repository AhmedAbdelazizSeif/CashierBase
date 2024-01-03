#  Copyright (c) 2023.
#

# with this one from Cashier/CashierFunctions/comparison_pair.py:
# Path: Cashier/CashierFunctions/comparison_pair.py

def comparison_pair(value, comparison_value):
    return ((value - comparison_value) / comparison_value) * 100 if comparison_value else 0.00
