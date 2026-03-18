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

from orders.models import Order, OrderItem
from .models import Cart
from notifications.models import Notification
from payments.models import Payment

# Initialize Razorpay client
RAZORPAY_KEY_ID = getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_YOUR_KEY_ID')
RAZORPAY_KEY_SECRET = getattr(settings, 'RAZORPAY_KEY_SECRET', 'YOUR_KEY_SECRET')

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@login_required
def create_razorpay_order(request):
    """Create Razorpay order from cart (not database order yet)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Get cart
        cart = Cart.objects.get(user=request.user)
        if not cart.cartitem_set.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get shipping address from session
        shipping_address_id = request.session.get('checkout_address_id')
        if not shipping_address_id:
            return JsonResponse({'error': 'No shipping address selected'}, status=400)
        
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
        
        # Store order details in session for verification
        request.session['pending_payment'] = {
            'razorpay_order_id': razorpay_order['id'],
            'amount': float(cart.get_cart_total),
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
def verify_razorpay_payment(request):
    """Verify payment and create order in database"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        
        print(f"\n=== RAZORPAY PAYMENT VERIFICATION ===")
        print(f"Payment ID: {razorpay_payment_id}")
        print(f"Order ID: {razorpay_order_id}")
        print(f"Received Signature: {razorpay_signature}")
        print(f"Key Secret: {RAZORPAY_KEY_SECRET}")
        
        # Verify signature using Razorpay's method
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        print(f"Message to sign: {message}")
        
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        print(f"Generated Signature: {generated_signature}")
        print(f"Signatures Match: {generated_signature == razorpay_signature}")
        
        if generated_signature != razorpay_signature:
            print("❌ Signature mismatch!")
            return JsonResponse({
                'error': 'Payment verification failed. Please contact support.',
                'success': False
            }, status=400)
        
        # Get cart
        cart = Cart.objects.get(user=request.user)
        if not cart.cartitem_set.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get shipping address from session
        shipping_address_id = request.session.get('checkout_address_id')
        shipping_address = request.user.shippingaddress_set.filter(id=shipping_address_id).first()
        if not shipping_address:
            return JsonResponse({'error': 'Invalid shipping address'}, status=400)
        
        # Validate stock before creating order
        for cart_item in cart.cartitem_set.all():
            if cart_item.quantity > cart_item.product.stock:
                return Response({
                    'error': f'Sorry, only {cart_item.product.stock} units of {cart_item.product.name} are available'
                }, status=400)
        
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
            if 'pending_payment' in request.session:
                del request.session['pending_payment']
            if 'checkout_address_id' in request.session:
                del request.session['checkout_address_id']
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': 'Payment successful'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def process_dummy_payment(request):
    """Process dummy payment for testing (instant approval)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Get cart
        cart = Cart.objects.get(user=request.user)
        if not cart.cartitem_set.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Get shipping address from session
        shipping_address_id = request.session.get('checkout_address_id')
        shipping_address = request.user.shippingaddress_set.filter(id=shipping_address_id).first()
        if not shipping_address:
            return JsonResponse({'error': 'Invalid shipping address'}, status=400)
        
        # Validate stock before creating order
        for cart_item in cart.cartitem_set.all():
            if cart_item.quantity > cart_item.product.stock:
                return JsonResponse({
                    'error': f'Sorry, only {cart_item.product.stock} units of {cart_item.product.name} are available'
                }, status=400)
        
        # Create order in database (credit card payment)
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.get_cart_total,
                shipping_address=shipping_address,
                payment_method='credit_card',
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
                payment_method='credit_card',
                status='completed',
                payment_details={
                    'transaction_id': f'CC_{order.id}_{int(cart.get_cart_total * 100)}',
                    'payment_gateway': 'credit_card'
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
            if 'pending_payment' in request.session:
                del request.session['pending_payment']
            if 'checkout_address_id' in request.session:
                del request.session['checkout_address_id']
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'message': 'Payment successful'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
