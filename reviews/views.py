from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ProductReview
from products.models import Product
from orders.models import Order

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased and received the product
    delivered_orders = Order.objects.filter(
        user=request.user,
        status='delivered',
        items__product=product
    )
    
    if not delivered_orders.exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'You can only review products from delivered orders.'
            })
        messages.error(request, 'You can only review products from delivered orders.')
        return redirect('products:product_detail', product_id=product_id)
    
    # Check if user already reviewed this product
    if ProductReview.objects.filter(user=request.user, product=product).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'message': 'You have already reviewed this product'
            })
        messages.error(request, 'You have already reviewed this product')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Review added successfully'
            })
        
        messages.success(request, 'Review added successfully')
        return redirect('products:product_detail', product_id=product_id)
    
    return render(request, 'reviews/add_review.html', {'product': product})

@login_required
def view_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    review = get_object_or_404(ProductReview, product=product, user=request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'review': {
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_at.strftime('%b %d, %Y')
            }
        })
    
    return render(request, 'reviews/view_review.html', {'review': review, 'product': product})