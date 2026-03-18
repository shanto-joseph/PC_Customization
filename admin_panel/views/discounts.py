from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from products.models import Discount

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_discounts(request):
    """View for managing discounts"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                Discount.objects.create(
                    code=request.POST.get('code'),
                    discount_type=request.POST.get('discount_type'),
                    discount_value=request.POST.get('discount_value'),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date'),
                    usage_limit=request.POST.get('usage_limit', 0),
                    is_active=request.POST.get('is_active', False) == 'on'
                )
                
                messages.success(request, 'Discount added successfully')
            except Exception as e:
                messages.error(request, f'Error creating discount: {str(e)}')
                
        elif action == 'update':
            try:
                discount = get_object_or_404(Discount, id=request.POST.get('discount_id'))
                old_code = discount.code
                
                discount.code = request.POST.get('code')
                discount.discount_type = request.POST.get('discount_type')
                discount.discount_value = request.POST.get('discount_value')
                discount.start_date = request.POST.get('start_date')
                discount.end_date = request.POST.get('end_date')
                discount.usage_limit = request.POST.get('usage_limit', 0)
                discount.is_active = request.POST.get('is_active', False) == 'on'
                discount.save()
                
                messages.success(request, 'Discount updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating discount: {str(e)}')
                
        elif action == 'delete':
            try:
                discount = get_object_or_404(Discount, id=request.POST.get('discount_id'))
                code = discount.code
                discount.delete()
                
                messages.success(request, 'Discount deleted successfully')
            except Exception as e:
                messages.error(request, f'Error deleting discount: {str(e)}')
    
    discounts = Discount.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/discounts/list.html', {'discounts': discounts})

@login_required
@user_passes_test(is_admin)
def discount_detail(request, discount_id):
    """Get discount details for editing"""
    discount = get_object_or_404(Discount, id=discount_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': discount.id,
            'code': discount.code,
            'discount_type': discount.discount_type,
            'discount_value': str(discount.discount_value),
            'start_date': discount.start_date.strftime('%Y-%m-%d'),
            'end_date': discount.end_date.strftime('%Y-%m-%d'),
            'usage_limit': discount.usage_limit,
            'is_active': discount.is_active
        }
        return JsonResponse(data)
    return render(request, 'admin_panel/discounts/detail.html', {'discount': discount})
