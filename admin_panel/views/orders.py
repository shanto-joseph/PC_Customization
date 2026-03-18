from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order
from notifications.models import Notification
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_orders(request):
    """View for managing orders"""
    # Get filters from request
    status = request.GET.get('status')
    date_range = request.GET.get('date_range')
    search = request.GET.get('search')
    
    # Base queryset
    orders = Order.objects.all()
    
    # Apply filters
    if status:
        orders = orders.filter(status=status)
        
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            orders = orders.filter(created_at__date=today)
        elif date_range == 'week':
            week_ago = today - timedelta(days=7)
            orders = orders.filter(created_at__date__gte=week_ago)
        elif date_range == 'month':
            month_ago = today - timedelta(days=30)
            orders = orders.filter(created_at__date__gte=month_ago)
            
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    # Order by most recent first
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
        'current_status': status,
        'current_date_range': date_range,
        'search_query': search
    }
    
    return render(request, 'admin_panel/orders/list.html', context)

@login_required
@user_passes_test(is_admin)
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_panel/orders/detail.html', {'order': order})

@login_required
@user_passes_test(is_admin)
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        old_status = order.status
        status = request.POST.get('status')
        
        if status not in dict(Order.STATUS_CHOICES):
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
        
        order.status = status
        order.save()
        
        # Notify customer
        Notification.create_notification(
            user=order.user,
            type='order_status',
            title='Order Status Updated',
            message=f'Your order #{order.id} status has been updated to {order.get_status_display()}',
            link=f'/orders/{order.id}/'
        )
        
        messages.success(request, 'Order status updated successfully')
        return JsonResponse({'success': True})
        
    return JsonResponse({'success': False}, status=405)