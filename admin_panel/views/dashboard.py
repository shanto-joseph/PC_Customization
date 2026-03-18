from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from orders.models import Order
from customization.models import CustomPC
from support.models import SupportTicket
from products.models import Product
from admin_panel.models import StoreAnalytics

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view with real-time analytics"""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Get orders data
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    total_orders = Order.objects.count()
    monthly_orders = Order.objects.filter(created_at__date__gte=thirty_days_ago).count()
    
    # Calculate revenue
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    monthly_revenue = Order.objects.filter(
        status='delivered',
        created_at__date__gte=thirty_days_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Get user statistics
    total_customers = User.objects.filter(role__name='customer').count()
    new_customers = User.objects.filter(
        role__name='customer',
        date_joined__date__gte=thirty_days_ago
    ).count()
    
    # Get custom builds data
    total_builds = CustomPC.objects.count()
    pending_builds = CustomPC.objects.filter(status='pending').count()
    
    # Get support tickets
    recent_tickets = SupportTicket.objects.all().order_by('-created_at')[:5]
    open_tickets = SupportTicket.objects.filter(status='open').count()
    
    # Get product performance
    product_performance = Product.objects.annotate(
        orders=Count('orderitem'),
        revenue=Sum('orderitem__price')
    ).order_by('-revenue')[:5]
    
    # Calculate growth percentages
    previous_month = today - timedelta(days=60)
    previous_month_revenue = Order.objects.filter(
        status='delivered',
        created_at__date__range=[previous_month, thirty_days_ago]
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    revenue_growth = ((monthly_revenue - previous_month_revenue) / previous_month_revenue * 100) if previous_month_revenue > 0 else 0
    
    context = {
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'revenue_growth': revenue_growth,
        'total_orders': total_orders,
        'monthly_orders': monthly_orders,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'total_builds': total_builds,
        'pending_builds': pending_builds,
        'open_tickets': open_tickets,
        'recent_orders': recent_orders,
        'recent_tickets': recent_tickets,
        'product_performance': product_performance,
        'current_date': today,
        'current_time': timezone.now().time()
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    """Admin profile view"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('admin_panel:profile')
    
    return render(request, 'admin_panel/profile.html')