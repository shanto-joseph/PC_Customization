"""
Admin panel views module.
"""

# Import all views from the views package
from .views.dashboard import admin_dashboard, admin_profile
from .views.users import manage_users, user_detail
from .views.staff import manage_staff, staff_detail
from .views.products import manage_products, product_detail
from .views.orders import manage_orders, order_detail, update_order_status
from .views.custom_builds import manage_custom_builds, build_detail, update_build_status
from .views.categories import manage_categories, category_detail
from .views.brands import manage_brands, brand_detail
from .views.reviews import manage_reviews
from .views.support import manage_support, ticket_detail, respond_to_ticket, update_ticket_status
from .views.analytics import analytics_dashboard
from .views.discounts import manage_discounts, discount_detail

# Re-export all views
__all__ = [
    # Dashboard
    'admin_dashboard',
    'admin_profile',
    
    # Users
    'manage_users',
    'user_detail',
    
    # Staff
    'manage_staff',
    'staff_detail',
    
    # Products
    'manage_products',
    'product_detail',
    
    # Orders
    'manage_orders',
    'order_detail',
    'update_order_status',
    
    # Custom Builds
    'manage_custom_builds',
    'build_detail',
    'update_build_status',
    
    # Categories
    'manage_categories',
    'category_detail',
    
    # Brands
    'manage_brands',
    'brand_detail',
    
    # Reviews
    'manage_reviews',
    
    # Support
    'manage_support',
    'ticket_detail',
    'respond_to_ticket',
    'update_ticket_status',
    
    # Analytics
    'analytics_dashboard',
    
    # Discounts
    'manage_discounts',
    'discount_detail',
]