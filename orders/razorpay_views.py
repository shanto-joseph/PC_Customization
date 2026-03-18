from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.conf import settings
import razorpay
import hmac
import hashlib
import json

from .models import Order, OrderItem
from cart.models import Cart
from notifications.models import Notification
from payments.models import Payment

# Initialize Razorpay client
# Test Mode Keys
RAZORPAY_KEY_ID = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_YOUR_KEY_ID')
RAZORPAY_KEY_SECRET = getattr(settings, 'RAZORPAY_KEY_SECRET', 'YOUR_KEY_SECRET')

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@login_required
def create_razorpay_order(request, order_id):
    """Create Razorpay order (not database order yet)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        shipping_address_id = data.get('shipping_address_id')
        
        # Get cart
        cart = Cart.objects.get(user=request.user)
        if not cart.cartitem_set.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Validate shipping address
        shipping_address = request.user.shippingaddress_set.filter(id=shipping_address_id).first()
        if not shipping_address:
            return JsonResponse({'error': 'Invalid shipping address'}, status=400)
        
        # Calculate amount
        amount = int(cart.get_cart_total * 100)  # Convert to paise
        
        # Create Razorpay order
        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })
        
        # Store order details in session for later
        request.session['pending_order'] = {
            'razorpay_order_id': razorpay_order['id'],
            'amount': cart.get_cart_total,
            'shipping_address_id': shipping_address_id
        }
        
        return JsonResponse({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@csrf_exempt
def verify_payment(request, order_id):
    """Verify payment and create order in database"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        shipping_address_id = data.get('shipping_address_id')
        
        # Verify signature
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            return JsonResponse({'error': 'Invalid payment signature'}, status=400)
        
        # Get cart
        cart = Cart.objects.get(user=request.user)
        if not cart.cartitem_set.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get shipping address
        shipping_address = request.user.shippingaddress_set.filter(id=shipping_address_id).first()
        if not shipping_address:
            return JsonResponse({'error': 'Invalid shipping address'}, status=400)
        
        # Create order in database (AFTER successful payment)
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.get_cart_total,
                shipping_address=shipping_address,
                payment_method='razorpay',
                payment_status='completed',
                status='processing'
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
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method='upi',
                status='completed',
                payment_details={
                    'transaction_id': razorpay_payment_id,
                    'razorpay_order_id': razorpay_order_id,
                    'payment_gateway': 'razorpay'
                }
            )
            
            # Clear cart
            cart.cartitem_set.all().delete()
            cart.coupon = None
            cart.save()
            
            # Create notification
            Notification.create_notification(
                user=request.user,
                type='order_status',
                title='Order Placed Successfully',
                message=f'Your order #{order.id} has been placed and payment received.',
                link=f'/orders/track/{order.id}/'
            )
            
            # Clear session
            if 'pending_order' in request.session:
                del request.session['pending_order']
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': 'Payment successful'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
