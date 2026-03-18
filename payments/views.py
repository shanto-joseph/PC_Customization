from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order
from customization.models import CustomPC
from notifications.models import Notification
from accounts.models import User
from .models import Payment
import json

@login_required
def process_payment(request, payment_type, object_id):
    """Process payment for either order or custom PC"""
    if payment_type == 'order':
        obj = get_object_or_404(Order, id=object_id, user=request.user)
        amount = obj.total_amount
    elif payment_type == 'custom_pc':
        obj = get_object_or_404(CustomPC, id=object_id, user=request.user)
        amount = obj.get_total_price
    else:
        messages.error(request, 'Invalid payment type')
        return redirect('home')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Collect payment details based on method
        payment_details = {}
        if payment_method == 'razorpay':
            payment_details = {
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_order_id': request.POST.get('razorpay_order_id'),
                'razorpay_signature': request.POST.get('razorpay_signature'),
            }
        elif payment_method == 'credit_card':
            # For demo purposes, store masked card details
            card_number = request.POST.get('card_number', '')
            masked_card = '**** **** **** ' + card_number[-4:] if len(card_number) >= 4 else '****'
            payment_details = {
                'card_number': masked_card,
                'card_name': request.POST.get('card_name'),
                'expiry_date': request.POST.get('expiry_date'),
                'payment_type': 'demo_credit_card'
            }
        
        # Create payment record
        payment = Payment.objects.create(
            order=obj if payment_type == 'order' else None,
            custom_pc=obj if payment_type == 'custom_pc' else None,
            payment_method=payment_method,
            amount=amount,
            status='completed',
            payment_details=payment_details
        )
        
        # Update object status
        if payment_type == 'order':
            obj.status = 'processing'
            obj.payment_status = 'completed'
            
            # Notify staff
            staff_users = User.objects.filter(role__name='staff')
            for staff in staff_users:
                Notification.create_notification(
                    user=staff,
                    type='order_status',
                    title='New Paid Order',
                    message=f'Order #{obj.id} has been paid and needs processing',
                    link=f'/staff/orders/{obj.id}/'
                )
        else:
            obj.status = 'paid'
            
            # Notify staff
            staff_users = User.objects.filter(role__name='staff')
            for staff in staff_users:
                Notification.create_notification(
                    user=staff,
                    type='build_paid',
                    title='New Paid Build',
                    message=f'Custom PC build #{obj.id} has been paid and needs assembly',
                    link=f'/staff/builds/{obj.id}/'
                )
        
        obj.save()
        
        messages.success(request, 'Payment processed successfully')
        return redirect('payments:payment_success')
    
    from django.conf import settings
    
    return render(request, 'payments/process_payment.html', {
        'object': obj,
        'payment_type': payment_type,
        'amount': amount,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    })

@login_required
def payment_success(request):
    """Payment success view"""
    return render(request, 'payments/payment_success.html')

@login_required
def payment_cancel(request):
    """Payment cancelled view"""
    return render(request, 'payments/payment_cancel.html')