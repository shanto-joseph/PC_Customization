from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .models import Cart, CartItem
from products.models import Product, Discount
from django.utils import timezone
import json

@login_required
def cart(request):
    """Display cart contents"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request):
    """Add a product to cart"""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if product is already in cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        messages.success(request, f"{product.name} added to cart")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f"{product.name} added to cart",
                'cart_total': float(cart.get_cart_total),
                'cart_items_count': cart.cartitem_set.count()
            })
    
    return redirect('cart:cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from cart")
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart, created = Cart.objects.get_or_create(user=request.user)
        return JsonResponse({
            'status': 'success',
            'message': f"{product_name} removed from cart",
            'cart_total': float(cart.get_cart_total),
            'cart_subtotal': float(cart.get_subtotal),
            'cart_discount': float(cart.get_discount_amount),
            'cart_items_count': cart.cartitem_set.count()
        })
    
    return redirect('cart:cart')

@login_required
def update_cart_quantity(request, item_id):
    """Update cart item quantity"""
    import json
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        # Handle JSON body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        else:
            quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully")
            item_total = cart_item.get_total
        else:
            product_name = cart_item.product.name
            cart_item.delete()
            messages.success(request, f"{product_name} removed from cart")
            item_total = 0
    except (ValueError, json.JSONDecodeError):
        messages.error(request, "Invalid quantity")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity'})
        return redirect('cart:cart')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'status': 'success',
            'cart_total': float(cart.get_cart_total),
            'cart_subtotal': float(cart.get_subtotal),
            'cart_discount': float(cart.get_discount_amount),
            'item_total': float(item_total),
            'cart_items_count': cart.cartitem_set.count()
        })
    
    return redirect('cart:cart')

@login_required
def apply_coupon(request):
    """Apply a coupon code to the cart"""
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            discount = Discount.objects.get(
                code=code,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
                is_active=True
            )
            
            cart = Cart.objects.get(user=request.user)
            cart.coupon = discount
            cart.save()
            
            messages.success(request, "Coupon applied successfully")
        except Discount.DoesNotExist:
            messages.error(request, "Invalid or expired coupon code")
    
    return redirect('cart:cart')

@login_required
def remove_coupon(request):
    """Remove coupon from cart"""
    cart = Cart.objects.get(user=request.user)
    cart.coupon = None
    cart.save()
    
    messages.success(request, "Coupon removed successfully")
    return redirect('cart:cart')

@login_required
def checkout(request):
    """Proceed to checkout"""
    cart = Cart.objects.get(user=request.user)
    
    if not cart.cartitem_set.exists():
        messages.error(request, "Your cart is empty")
        return redirect('cart:cart')
    
    # Check if all items are in stock
    for item in cart.cartitem_set.all():
        if item.quantity > item.product.stock:
            messages.error(
                request, 
                f"Sorry, only {item.product.stock} units of {item.product.name} are available"
            )
            return redirect('cart:cart')
    
    if request.method == 'POST':
        shipping_address_id = request.POST.get('shipping_address_id')
        if not shipping_address_id:
            messages.error(request, "Please select a shipping address")
            return redirect('cart:cart')
        
        # Pass the shipping address ID to create_order
        request.POST = request.POST.copy()  # Make POST mutable
        request.POST['shipping_address_id'] = shipping_address_id
        return redirect('orders:create_order')
    
    return render(request, 'cart/checkout.html', {'cart': cart})


@login_required
def prepare_checkout(request):
    """Prepare checkout by storing address in session"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            shipping_address_id = data.get('shipping_address_id')
            
            # Validate address belongs to user
            address = request.user.shippingaddress_set.filter(id=shipping_address_id).first()
            if not address:
                return JsonResponse({'error': 'Invalid shipping address'}, status=400)
            
            # Store in session
            request.session['checkout_address_id'] = shipping_address_id
            
            # Return payment URL
            return JsonResponse({
                'success': True,
                'payment_url': reverse('cart:payment_page')
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=405)

@login_required
def payment_page(request):
    """Show payment page and process payment like Custom PC Build"""
    cart = Cart.objects.get(user=request.user)
    
    if not cart.cartitem_set.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart')
    
    # Get address from session
    address_id = request.session.get('checkout_address_id')
    if not address_id:
        messages.error(request, 'Please select a shipping address')
        return redirect('cart:checkout')
    
    shipping_address = request.user.shippingaddress_set.filter(id=address_id).first()
    if not shipping_address:
        messages.error(request, 'Invalid shipping address')
        return redirect('cart:checkout')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Validate stock levels before creating order
        for cart_item in cart.cartitem_set.all():
            if cart_item.quantity > cart_item.product.stock:
                messages.error(
                    request, 
                    f'Sorry, only {cart_item.product.stock} units of {cart_item.product.name} are available'
                )
                return redirect('cart:cart')
        
        try:
            from django.db import transaction
            from orders.models import Order, OrderItem
            from payments.models import Payment
            from notifications.models import Notification
            from accounts.models import User
            
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    total_amount=cart.get_cart_total,
                    shipping_address=shipping_address,
                    payment_method=payment_method,
                    status='processing',
                    payment_status='completed'
                )
                
                # Create order items and update stock
                for cart_item in cart.cartitem_set.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    # Update product stock
                    cart_item.product.stock -= cart_item.quantity
                    cart_item.product.save()
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='completed'
                )
                
                # Clear cart
                cart.cartitem_set.all().delete()
                cart.coupon = None
                cart.save()
                
                # Clear session
                if 'checkout_address_id' in request.session:
                    del request.session['checkout_address_id']
                
                # Notify staff
                staff_users = User.objects.filter(role__name='staff')
                for staff in staff_users:
                    Notification.create_notification(
                        user=staff,
                        type='order_status',
                        title='New Paid Order',
                        message=f'Order #{order.id} has been paid and needs processing',
                        link=f'/staff/orders/{order.id}/'
                    )
                
                # Notify customer
                Notification.create_notification(
                    user=request.user,
                    type='order_status',
                    title='Order Placed Successfully',
                    message=f'Your order #{order.id} has been placed and payment confirmed',
                    link=f'/orders/track/{order.id}/'
                )
                
                messages.success(request, 'Order placed and payment processed successfully')
                return redirect('cart:payment_success')
                
        except Exception as e:
            messages.error(request, f'An error occurred while processing your order: {str(e)}')
            return redirect('cart:payment_page')
    
    # Get Razorpay key from settings
    from django.conf import settings
    
    context = {
        'cart': cart,
        'shipping_address': shipping_address,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID
    }
    
    return render(request, 'cart/payment.html', context)


@login_required
def payment_success(request):
    """Payment success view for cart orders"""
    return render(request, 'cart/payment_success.html')


@login_required
def payment_cancel(request):
    """Payment cancelled view for cart orders"""
    return render(request, 'cart/payment_cancel.html')
