from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from products.models import Product, Category, Brand
from orders.models import Order
from customization.models import CustomPC
from support.models import SupportTicket, TicketResponse
from notifications.models import Notification
import json

def is_staff(user):
    return user.is_authenticated and (user.is_staff_member or user.is_admin)

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    """Staff dashboard view"""
    context = {
        'pending_builds': CustomPC.objects.filter(assigned_staff=request.user, status='pending').count(),
        'assigned_builds': CustomPC.objects.filter(assigned_staff=request.user).count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'pending_tickets': SupportTicket.objects.filter(assigned_staff=request.user, status='open').count(),
        'recent_builds': CustomPC.objects.filter(assigned_staff=request.user).order_by('-created_at')[:5],
        'recent_orders': Order.objects.all().order_by('-created_at')[:5],
        'recent_tickets': SupportTicket.objects.filter(assigned_staff=request.user).order_by('-created_at')[:5]
    }
    return render(request, 'staff_panel/dashboard.html', context)

@login_required
@user_passes_test(is_staff)
def manage_products(request, product_id=None):
    """Staff view for managing products"""
    if product_id and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'category': product.category_id,
            'brand': product.brand_id,
            'stock': product.stock,
            'image_url': product.image.url if product.image else None
        }
        return JsonResponse(data)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                product = Product.objects.create(
                    name=request.POST.get('name'),
                    description=request.POST.get('description'),
                    price=request.POST.get('price'),
                    category_id=request.POST.get('category'),
                    brand_id=request.POST.get('brand'),
                    stock=request.POST.get('stock', 0)
                )
                
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                    product.save()
                
                messages.success(request, 'Product added successfully')
            except Exception as e:
                messages.error(request, f'Error adding product: {str(e)}')
        
        elif action == 'update':
            try:
                product_id = request.POST.get('product_id')
                product = get_object_or_404(Product, id=product_id)
                
                product.name = request.POST.get('name')
                product.description = request.POST.get('description')
                product.price = request.POST.get('price')
                product.category_id = request.POST.get('category')
                product.brand_id = request.POST.get('brand')
                product.stock = request.POST.get('stock', 0)
                
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                
                product.save()
                messages.success(request, 'Product updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        
        elif action == 'delete':
            try:
                product_id = request.POST.get('product_id')
                product = get_object_or_404(Product, id=product_id)
                product.delete()
                messages.success(request, 'Product deleted successfully')
            except Exception as e:
                messages.error(request, f'Error deleting product: {str(e)}')
        
        return redirect('staff_panel:products')
    
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    return render(request, 'staff_panel/products/list.html', {
        'products': products,
        'categories': categories,
        'brands': brands
    })

@login_required
@user_passes_test(is_staff)
def edit_product(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': float(product.price),
            'category': product.category_id,
            'brand': product.brand_id,
            'stock': product.stock,
            'image_url': product.image.url if product.image else None
        }
        return JsonResponse(data)
    
    if request.method == 'POST':
        try:
            product.name = request.POST.get('name')
            product.description = request.POST.get('description')
            product.price = request.POST.get('price')
            product.category_id = request.POST.get('category')
            product.brand_id = request.POST.get('brand')
            product.stock = request.POST.get('stock', 0)
            
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            
            product.save()
            messages.success(request, 'Product updated successfully')
            return redirect('staff_panel:products')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('staff_panel:products')
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'staff_panel/products/edit.html', {
        'product': product,
        'categories': categories,
        'brands': brands
    })

@login_required
@user_passes_test(is_staff)
def delete_product(request, product_id):
    """Delete product"""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
    return redirect('staff_panel:products')

@login_required
@user_passes_test(is_staff)
def check_stock_levels(request):
    """Check for low stock products"""
    low_stock = Product.objects.filter(stock__lte=10)
    return JsonResponse({
        'low_stock': [{
            'id': product.id,
            'name': product.name,
            'stock': product.stock
        } for product in low_stock]
    })

@login_required
@user_passes_test(is_staff)
def manage_builds(request):
    """Staff view for managing custom PC builds"""
    builds = CustomPC.objects.filter(assigned_staff=request.user).order_by('-created_at')
    return render(request, 'staff_panel/builds/list.html', {'builds': builds})

@login_required
@user_passes_test(is_staff)
def build_detail(request, build_id):
    """View custom PC build details"""
    build = get_object_or_404(CustomPC, id=build_id, assigned_staff=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            status = request.POST.get('status')
            assembly_notes = request.POST.get('assembly_notes', '')
            rejection_reason = request.POST.get('rejection_reason', '')
            
            build.status = status
            build.assembly_notes = assembly_notes
            
            if status == 'rejected':
                build.rejection_reason = rejection_reason
                Notification.create_notification(
                    user=build.user,
                    type='build_status',
                    title='Build Request Rejected',
                    message=f'Your custom PC build request has been rejected. Reason: {rejection_reason}',
                    link=f'/customization/build/{build.id}/'
                )
            elif status == 'approved':
                Notification.create_notification(
                    user=build.user,
                    type='build_status',
                    title='Build Approved - Payment Required',
                    message=f'Your custom PC build has been approved. Please proceed with payment.',
                    link=f'/customization/build/{build.id}/'
                )
            
            build.save()
            messages.success(request, 'Build status updated successfully')
            
    return render(request, 'staff_panel/builds/detail.html', {'build': build})

@login_required
@user_passes_test(is_staff)
def update_build_status(request, build_id):
    """Update custom PC build status"""
    if request.method == 'POST':
        build = get_object_or_404(CustomPC, id=build_id)
        old_status = build.status
        status = request.POST.get('status')
        
        if not status:
            return JsonResponse({'success': False, 'message': 'Status cannot be empty'}, status=400)
            
        if status not in dict(CustomPC.STATUS_CHOICES):
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
        
        build.status = status
        if request.POST.get('assembly_notes'):
            build.assembly_notes = request.POST.get('assembly_notes')
            
        if status == 'rejected' and request.POST.get('rejection_reason'):
            build.rejection_reason = request.POST.get('rejection_reason')
            
        build.save()
        
        message = f'Your custom PC build status has been updated to {status}'
        if status == 'rejected' and build.rejection_reason:
            message = f'Your custom PC build has been rejected. Reason: {build.rejection_reason}'
            
        Notification.create_notification(
            user=build.user,
            type='build_status',
            title='Build Status Updated',
            message=message,
            link=f'/customization/build/{build.id}/'
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_staff)
def manage_tickets(request):
    """Staff view for managing support tickets"""
    tickets = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'staff_panel/support/list.html', {'tickets': tickets})

@login_required
@user_passes_test(is_staff)
def ticket_detail(request, ticket_id):
    """Staff view for ticket details"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    return render(request, 'staff_panel/support/detail.html', {'ticket': ticket})

@login_required
@user_passes_test(is_staff)
def respond_to_ticket(request, ticket_id):
    """Add response to support ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            response = TicketResponse.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            
            Notification.create_notification(
                user=ticket.user,
                type='support',
                title='New Response on Your Ticket',
                message=f'Staff responded to your ticket #{ticket.id}',
                link=f'/support/ticket/{ticket.id}/'
            )
            
            messages.success(request, 'Response added successfully')
            
    return redirect('staff_panel:ticket_detail', ticket_id=ticket_id)

@login_required
@user_passes_test(is_staff)
def update_ticket_status(request, ticket_id):
    """Update support ticket status"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        old_status = ticket.status
        status = request.POST.get('status')
        
        ticket.status = status
        ticket.save()
        
        Notification.create_notification(
            user=ticket.user,
            type='support',
            title='Support Ticket Status Updated',
            message=f'Your ticket #{ticket.id} status has been updated to {status}',
            link=f'/support/ticket/{ticket.id}/'
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@user_passes_test(is_staff)
def manage_orders(request):
    """Staff view for managing orders"""
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'staff_panel/orders/list.html', {'orders': orders})

@login_required
@user_passes_test(is_staff)
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'staff_panel/orders/detail.html', {'order': order})

@login_required
@user_passes_test(is_staff)
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            status = data.get('status')
        else:
            status = request.POST.get('status')
        
        if not status:
            return JsonResponse({'success': False, 'message': 'Status is required'}, status=400)
        
        order.status = status
        order.save()
        
        Notification.create_notification(
            user=order.user,
            type='order_status',
            title='Order Status Updated',
            message=f'Your order #{order.id} status has been updated to {status}',
            link=f'/orders/{order.id}/'
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

@login_required
@user_passes_test(is_staff)
def profile(request):
    """Staff profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('staff_panel:profile')
    
    return render(request, 'staff_panel/profile.html')

@login_required
@user_passes_test(is_staff)
def notifications(request):
    """View staff notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'staff_panel/notifications/list.html', {'notifications': notifications})

@login_required
@user_passes_test(is_staff)
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(is_staff)
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
@user_passes_test(is_staff)
def get_unread_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})