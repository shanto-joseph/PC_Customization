from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category, Brand
from reviews.models import ProductReview
from orders.models import Order

def home(request):
    """Home page view"""
    featured_products = Product.objects.filter(is_prebuilt=True)[:4]
    latest_products = Product.objects.all().order_by('-created_at')[:8]
    brands = Brand.objects.all()
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'brands': brands
    }
    return render(request, 'products/home.html', context)

def product_list(request):
    """Display all products with filtering options"""
    products = Product.objects.all()
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id and category_id.isdigit():
        products = products.filter(category_id=int(category_id))
    
    # Filter by brand
    brand_id = request.GET.get('brand')
    if brand_id and brand_id.isdigit():
        products = products.filter(brand_id=int(brand_id))
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    """Display product details and reviews"""
    product = get_object_or_404(Product, id=product_id)
    reviews = product.customer_reviews.all().order_by('-created_at')
    
    # Check if user has purchased the product
    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = Order.objects.filter(
            user=request.user,
            status='delivered',
            items__product=product
        ).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'has_purchased': has_purchased
    }
    return render(request, 'products/product_detail.html', context)

def category_products(request, category_id):
    """Display products by category"""
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'products/category_products.html', context)

def brand_products(request, brand_id):
    """Display products by brand"""
    brand = get_object_or_404(Brand, id=brand_id)
    products = Product.objects.filter(brand=brand)
    
    context = {
        'brand': brand,
        'products': products
    }
    return render(request, 'products/brand_products.html', context)

def search_products(request):
    """Search products"""
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )
    
    context = {
        'query': query,
        'products': products
    }
    return render(request, 'products/search_results.html', context)

def search_suggestions(request):
    """AJAX endpoint for search suggestions"""
    query = request.GET.get('q', '')
    suggestions = []
    
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )[:5]
        suggestions = [product.name for product in products]
    
    return JsonResponse({'suggestions': suggestions})

@login_required
def staff_products(request):
    """Staff view for managing products"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'brands': brands
    }
    return render(request, 'staff_panel/products/list.html', context)

@login_required
def staff_product_detail(request, product_id):
    """Staff view for product details"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    product = get_object_or_404(Product, id=product_id)
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'category': product.category_id,
        'brand': product.brand_id,
        'stock': product.stock,
        'image_url': product.image.url if product.image else None
    })

@login_required
def staff_delete_product(request, product_id):
    """Staff endpoint to delete product"""
    if not request.user.is_staff_member:
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return JsonResponse({'success': True})

@login_required
def check_stock_levels(request):
    """Staff endpoint to check low stock products"""
    if not request.user.is_staff_member:
        return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
    
    low_stock_products = Product.objects.filter(stock__lte=10)
    data = [{
        'id': product.id,
        'name': product.name,
        'stock': product.stock
    } for product in low_stock_products]
    
    return JsonResponse({'low_stock': data})

def api_product_list(request):
    """API endpoint for product list"""
    products = Product.objects.all()
    data = [{
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'stock': product.stock,
        'image_url': product.image.url if product.image else None
    } for product in products]
    return JsonResponse({'products': data})

def api_product_detail(request, product_id):
    """API endpoint for product details"""
    product = get_object_or_404(Product, id=product_id)
    data = {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': str(product.price),
        'category': {
            'id': product.category.id,
            'name': product.category.name
        },
        'brand': {
            'id': product.brand.id,
            'name': product.brand.name
        },
        'stock': product.stock,
        'image_url': product.image.url if product.image else None,
        'created_at': product.created_at.isoformat(),
        'updated_at': product.updated_at.isoformat()
    }
    return JsonResponse(data)