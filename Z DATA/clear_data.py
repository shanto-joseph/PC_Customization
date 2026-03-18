#!/usr/bin/env python3
"""
Script to clear all product-related data from the database.
"""

import os
import sys
import django

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pc_shop.settings')
django.setup()

from products.models import Product, Category, Brand
from orders.models import Order, OrderItem
from payments.models import Payment
from customization.models import CustomPC


def clear_all_data():
    """Clear all product-related data"""
    print("Clearing all product-related data from database...")
    
    # Clear custom PC builds first (they reference products)
    try:
        custom_pcs_deleted = CustomPC.objects.all().delete()
        print(f"Deleted {custom_pcs_deleted[0]} Custom PC builds.")
    except Exception as e:
        print(f"No Custom PC builds to delete or error: {e}")
    
    # Clear order items first (they reference products)
    try:
        items_deleted = OrderItem.objects.all().delete()
        print(f"Deleted {items_deleted[0]} Order Items.")
    except Exception as e:
        print(f"No Order Items to delete or error: {e}")
    
    # Clear payments
    try:
        payments_deleted = Payment.objects.all().delete()
        print(f"Deleted {payments_deleted[0]} Payments.")
    except Exception as e:
        print(f"No Payments to delete or error: {e}")

    # Clear orders
    try:
        orders_deleted = Order.objects.all().delete()
        print(f"Deleted {orders_deleted[0]} Orders.")
    except Exception as e:
        print(f"No Orders to delete or error: {e}")
    
    # Clear products
    products_deleted = Product.objects.all().delete()
    print(f"Deleted {products_deleted[0]} Products.")
    
    # Clear categories
    categories_deleted = Category.objects.all().delete()
    print(f"Deleted {categories_deleted[0]} Categories.")
    
    # Clear brands
    brands_deleted = Brand.objects.all().delete()
    print(f"Deleted {brands_deleted[0]} Brands.")
    
    print("\n✅ Success! All product-related data has been cleared from the database.")
    print("The database is now clean and ready for fresh data.")


if __name__ == '__main__':
    try:
        clear_all_data()
    except Exception as e:
        print(f"❌ Error clearing data: {str(e)}")
        sys.exit(1)