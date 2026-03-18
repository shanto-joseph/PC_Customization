from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Wishlist
from products.models import Product

@login_required
def wishlist(request):
    """Display user's wishlist items"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    """Add a product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if item already exists in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} has been added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to wishlist' if created else 'Product already in wishlist'
        })
    
    return redirect('products:product_detail', product_id=product_id)

@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from wishlist"""
    wishlist_item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    product_name = wishlist_item.product.name
    wishlist_item.delete()
    
    messages.success(request, f"{product_name} has been removed from your wishlist.")
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Product removed from wishlist'
        })
    
    return redirect('wishlist:wishlist')