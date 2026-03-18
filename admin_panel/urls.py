from django.urls import path
from . import views
from .views.dashboard import admin_dashboard, admin_profile
from .views.users import manage_users, user_detail
from .views.staff import manage_staff, staff_detail
from .views.products import manage_products, product_detail
from .views.orders import manage_orders, order_detail, update_order_status
from .views.custom_builds import manage_custom_builds, build_detail, update_build_status
from .views.categories import manage_categories, category_detail
from .views.brands import manage_brands, brand_detail
from .views.reviews import manage_reviews
from .views.support import (
    manage_support, ticket_detail, respond_to_ticket, 
    update_ticket_status, update_ticket_assignment
)
from .views.analytics import analytics_dashboard
from .views.discounts import manage_discounts, discount_detail

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard and Profile
    path('dashboard/', admin_dashboard, name='dashboard'),
    path('profile/', admin_profile, name='profile'),

    # User and Staff Management
    path('users/', manage_users, name='users'),
    path('users/<int:user_id>/', user_detail, name='user_detail'),
    path('staff/', manage_staff, name='staff'),
    path('staff/<int:staff_id>/', staff_detail, name='staff_detail'),

    # Product Management
    path('products/', manage_products, name='products'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),

    # Order Management
    path('orders/', manage_orders, name='orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', update_order_status, name='update_order_status'),

    # Custom PC Build Management
    path('custom-builds/', manage_custom_builds, name='custom_builds'),
    path('custom-builds/<int:build_id>/', build_detail, name='build_detail'),
    path('custom-builds/<int:build_id>/update-status/', update_build_status, name='update_build_status'),

    # Categories and Brands
    path('categories/', manage_categories, name='categories'),
    path('categories/<int:category_id>/', category_detail, name='category_detail'),
    path('brands/', manage_brands, name='brands'),
    path('brands/<int:brand_id>/', brand_detail, name='brand_detail'),

    # Review Management
    path('reviews/', manage_reviews, name='reviews'),

    # Support Management
    path('support/', manage_support, name='support'),
    path('support/<int:ticket_id>/', ticket_detail, name='ticket_detail'),
    path('support/<int:ticket_id>/respond/', respond_to_ticket, name='respond_to_ticket'),
    path('support/<int:ticket_id>/update-status/', update_ticket_status, name='update_ticket_status'),
    path('support/<int:ticket_id>/assign/', update_ticket_assignment, name='update_ticket_assignment'),

    # Analytics
    path('analytics/', analytics_dashboard, name='analytics'),

    # Discount Management
    path('discounts/', manage_discounts, name='discounts'),
    path('discounts/<int:discount_id>/', discount_detail, name='discount_detail'),
]