from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Public routes
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/category/<int:category_id>/', views.category_products, name='category_products'),
    path('products/brand/<int:brand_id>/', views.brand_products, name='brand_products'),
    path('products/search/', views.search_products, name='search_products'),
    path('products/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # Staff routes
    path('staff/products/', views.staff_products, name='staff_products'),
    path('staff/product/<int:product_id>/', views.staff_product_detail, name='staff_product_detail'),
    path('staff/product/<int:product_id>/delete/', views.staff_delete_product, name='staff_delete_product'),
    path('staff/check-stock/', views.check_stock_levels, name='check_stock_levels'),
    
    # API routes
    path('api/products/', views.api_product_list, name='api_product_list'),
    path('api/products/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
]
