from django.urls import path
from . import views

app_name = 'staff_panel'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Products Management
    path('products/', views.manage_products, name='products'),
    path('products/<int:product_id>/', views.manage_products, name='product_detail'),
    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('products/check-stock/', views.check_stock_levels, name='check_stock'),
    
    # Orders Management
    path('orders/', views.manage_orders, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Custom PC Builds
    path('builds/', views.manage_builds, name='builds'),
    path('builds/<int:build_id>/', views.build_detail, name='build_detail'),
    path('builds/<int:build_id>/update-status/', views.update_build_status, name='update_build_status'),
    
    # Support Tickets
    path('support/', views.manage_tickets, name='support_tickets'),
    path('support/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('support/<int:ticket_id>/respond/', views.respond_to_ticket, name='respond_to_ticket'),
    path('support/<int:ticket_id>/update-status/', views.update_ticket_status, name='update_ticket_status'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/unread-count/', views.get_unread_count, name='unread_count'),
]