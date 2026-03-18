from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from accounts.models import User
from products.models import Product, Category
from customization.models import CustomPC
from admin_panel.models import StoreAnalytics

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """View analytics dashboard with real data"""
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Daily analytics for the past 30 days
    daily_analytics = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total_sales=Sum('total_amount'),
        total_orders=Count('id')
    ).order_by('date')

    # Add new customers count to daily analytics
    for day in daily_analytics:
        day['new_customers'] = User.objects.filter(
            role__name='customer',
            date_joined__date=day['date']
        ).count()
    
    # Calculate totals
    total_revenue = Order.objects.filter(status='delivered').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    total_orders = Order.objects.count()
    total_customers = User.objects.filter(role__name='customer').count()
    total_products = Product.objects.count()
    
    # Category revenue analysis
    category_revenue = OrderItem.objects.values(
        'product__category__name'
    ).annotate(
        total=Sum(F('price') * F('quantity'))
    ).order_by('-total')
    
    # Product performance analysis
    product_performance = Product.objects.annotate(
        orders=Count('orderitem'),
        revenue=Sum(F('orderitem__price') * F('orderitem__quantity')),
        conversion_rate=ExpressionWrapper(
            Count('orderitem') * 100.0 / F('stock'),
            output_field=FloatField()
        )
    ).order_by('-revenue')[:10]

    # Add status based on revenue
    for product in product_performance:
        if product.revenue and product.revenue > 100000:
            product.status = 'high'
        elif product.revenue and product.revenue > 50000:
            product.status = 'medium'
        else:
            product.status = 'low'
    
    context = {
        'analytics': daily_analytics,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'category_revenue': category_revenue,
        'product_performance': product_performance,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'admin_panel/analytics/dashboard.html', context)
