from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import User, Role
from orders.models import Order
from customization.models import CustomPC
from support.models import SupportTicket

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """View for managing users"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                # Get appropriate role based on user type
                user_type = request.POST.get('user_type')
                role = Role.objects.get(name='staff' if user_type == 'staff' else 'customer')
                
                # Create new user
                user = User.objects.create_user(
                    username=request.POST.get('username'),
                    email=request.POST.get('email'),
                    password=request.POST.get('password'),
                    first_name=request.POST.get('first_name', ''),
                    last_name=request.POST.get('last_name', ''),
                    phone_number=request.POST.get('phone_number', ''),
                    role=role
                )
                messages.success(request, f'User {user.get_full_name() or user.email} has been added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding user: {str(e)}')
            
            return redirect('admin_panel:users')
            
        elif action == 'delete':
            user_id = request.POST.get('user_id')
            try:
                user = get_object_or_404(User, id=user_id)
                if user.id != request.user.id:  # Prevent self-deletion
                    user_name = user.get_full_name() or user.email
                    user.delete()
                    messages.success(request, f'User {user_name} has been deleted successfully.')
                else:
                    messages.error(request, 'You cannot delete your own account.')
            except Exception as e:
                messages.error(request, f'Error deleting user: {str(e)}')
            
            return redirect('admin_panel:users')
    
    # Get admin, staff and customer users separately
    admin_users = User.objects.filter(role__name='admin').order_by('-date_joined')
    staff_users = User.objects.filter(role__name='staff').order_by('-date_joined')
    customer_users = User.objects.filter(role__name='customer').order_by('-date_joined')
    
    return render(request, 'admin_panel/users/list.html', {
        'admin_users': admin_users,
        'staff_users': staff_users,
        'customer_users': customer_users
    })

@login_required
@user_passes_test(is_admin)
def user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Calculate activity summary
        orders = Order.objects.filter(user=user)
        custom_builds = CustomPC.objects.filter(user=user)
        support_tickets = SupportTicket.objects.filter(user=user)
        
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number or 'Not provided',
            'date_joined': user.date_joined.strftime('%b %d, %Y'),
            'total_orders': orders.count(),
            'total_purchases': sum(order.total_amount for order in orders),
            'custom_builds': custom_builds.count(),
            'support_tickets': support_tickets.count()
        }
        return JsonResponse(data)
    
    if request.method == 'POST':
        # Update user details
        try:
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.phone_number = request.POST.get('phone_number', '')
            user.save()
            messages.success(request, 'User details updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
        
        return redirect('admin_panel:user_detail', user_id=user.id)
    
    orders = Order.objects.filter(user=user)
    custom_builds = CustomPC.objects.filter(user=user)
    support_tickets = SupportTicket.objects.filter(user=user)
    
    context = {
        'user': user,
        'orders': orders,
        'custom_builds': custom_builds,
        'support_tickets': support_tickets
    }
    return render(request, 'admin_panel/users/detail.html', context)