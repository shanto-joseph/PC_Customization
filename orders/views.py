from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart
from notifications.models import Notification
from payments.models import Payment
from accounts.models import User
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/track_order.html', {'order': order})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    if not cart.cartitem_set.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart:cart')
    
    # Get shipping address from form data
    shipping_address_id = request.POST.get('shipping_address_id')
    if shipping_address_id:
        shipping_address = request.user.shippingaddress_set.filter(id=shipping_address_id).first()
    else:
        shipping_address = request.user.shippingaddress_set.filter(is_default=True).first()
    
    if not shipping_address:
        messages.error(request, 'Please select a shipping address')
        return redirect('cart:cart')
    
    # Validate stock levels
    for cart_item in cart.cartitem_set.all():
        if cart_item.quantity > cart_item.product.stock:
            messages.error(
                request, 
                f'Sorry, only {cart_item.product.stock} units of {cart_item.product.name} are available'
            )
            return redirect('cart:cart')
    
    try:
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.get_cart_total,
                shipping_address=shipping_address,
                payment_method=request.POST.get('payment_method')
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
            
            # Clear cart
            cart.cartitem_set.all().delete()
            
            # Create notification
            Notification.create_notification(
                user=request.user,
                type='order_status',
                title='Order Created Successfully',
                message=f'Your order #{order.id} has been created.',
                link=f'/orders/track/{order.id}/'
            )
            
            # Redirect to payment
            return redirect('orders:process_payment', order_id=order.id)
            
    except Exception as e:
        messages.error(request, 'An error occurred while creating your order. Please try again.')
        return redirect('cart:cart')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def process_payment(request, order_id):
    """Process payment for an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Validate order status
    if order.payment_status == 'completed':
        messages.error(request, 'This order has already been paid')
        return redirect('orders:order_detail', order_id=order.id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'razorpay':
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            payment_amount = int(order.total_amount * 100) # Convert to paise
            
            data = { 
                "amount": payment_amount, 
                "currency": "INR", 
                "receipt": str(order.id),
                "payment_capture": "1"
            }
            payment = client.order.create(data=data)
            
            context = {
                'order': order,
                'razorpay_order_id': payment['id'],
                'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
                'razorpay_amount': payment_amount,
                'currency': "INR",
                'callback_url': request.build_absolute_uri('/orders/payment/callback/'),
            }
            return render(request, 'orders/razorpay_checkout.html', context)
            
        try:
            with transaction.atomic():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    amount=order.total_amount,
                    status='completed'  # For demonstration, in production this would be handled by payment gateway
                )
                
                # Update order status
                order.status = 'processing'
                order.payment_status = 'completed'
                order.save()
                
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
                
                messages.success(request, 'Payment processed successfully')
                return redirect('orders:payment_success')
                
        except Exception as e:
            messages.error(request, 'An error occurred while processing your payment. Please try again.')
            return redirect('orders:process_payment', order_id=order.id)
    
    return render(request, 'orders/payment.html', {'order': order})

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify signature
            result = client.utility.verify_payment_signature(params_dict)
            
            if result is None: # Verify returns None on success, raises error on failure usually? 
                # Actually verify_payment_signature returns None on success (if no error), 
                # but older versions might return True.
                # Let's rely on try-except. 
                pass
            
            # Find the order via some mechanism? 
            # We don't have the order_id in POST directly unless we passed it in custom callback or stored in session.
            # But we can look up if we stored the razorpay_order_id on the order? 
            # Or we can pass it in 'notes' during creation but that's for razorpay dashboard.
            # The 'receipt' field was set to str(order.id).
            
            # Wait, verify_payment_signature raises an error if invalid.
            
            # Use 'receipt' to find order? No, client.order.create params are for creation.
            # We can't easily fetch the order from just these 3 params unless we query Razorpay or stored the RZ order ID locally.
            # Let's store RZ order ID in session in process_payment? Or simpler: 
            # In the razorpay_checkout.html, we form the callback POST. We can include the order ID there?
            # Standard RZ Checkout POSTs to callback_url with those 3 fields.
            # We will use the stored 'razorpay_order_id' to find the pending payment/order?
            # Creating a Payment model with the RZ order ID beforehand is better?
            
            # Simplest for now: 
            # Fetch the order by querying razorpay API with the order_id to get the receipt (which is our order ID)?
            # OR better: The razorpay order ID is unique. We could save it in the order model, OR 
            # we can pass 'order_id' in the callback URL? e.g. /orders/payment/callback/?order_id=123
            # But the POST comes from Razorpay form (client side).
            
            # Let's try to get order from retrieval of razorpay order details if needed, 
            # OR just pass it as a hidden field in the form generated by checkout.js if possible.
            # Actually, standard checkout.js 'handler' function allows us to control the submission.
            
            # I'll stick to: Store order_id in session? No, flaky.
            # I will fetch the order detail from Razorpay using the order_id.
            
            order_info = client.order.fetch(razorpay_order_id)
            internal_order_id = order_info['receipt']
            order = Order.objects.get(id=internal_order_id)
            
            with transaction.atomic():
                 # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method='razorpay',
                    amount=order.total_amount,
                    transaction_id=payment_id,
                    status='completed'
                )
                
                order.status = 'processing'
                order.payment_status = 'completed'
                order.save()
                
                # Notify staff
                staff_users = User.objects.filter(role__name='staff')
                for staff in staff_users:
                    Notification.create_notification(
                        user=staff,
                        type='order_status',
                        title='New Paid Order',
                        message=f'Order #{order.id} has been paid via Razorpay',
                        link=f'/staff/orders/{order.id}/'
                    )
            
            return redirect('orders:payment_success')
            
        except Exception as e:
            print(e)
            return render(request, 'orders/payment_cancel.html')
            
    return redirect('orders:payment_cancel')

@login_required
def payment_success(request):
    """Payment success view"""
    return render(request, 'orders/payment_success.html')

@login_required
def payment_cancel(request):
    """Payment cancelled view"""
    return render(request, 'orders/payment_cancel.html')

@login_required
def staff_orders(request):
    """Staff view for managing orders"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'staff_panel/orders/list.html', {'orders': orders})
