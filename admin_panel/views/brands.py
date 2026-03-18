from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from products.models import Brand

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_brands(request):
    """View for managing brands"""
    brands = Brand.objects.all()
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Add new brand
        if action == 'add':
            name = request.POST.get('name')
            description = request.POST.get('description')
            logo = request.FILES.get('logo')
            
            brand = Brand(name=name, description=description)
            if logo:
                brand.logo = logo
            brand.save()
            
            messages.success(request, f'Brand "{name}" has been added successfully')
            return redirect('admin_panel:brands')
            
        # Update existing brand
        elif action == 'update':
            brand_id = request.POST.get('brand_id')
            brand = get_object_or_404(Brand, id=brand_id)
            
            brand.name = request.POST.get('name')
            brand.description = request.POST.get('description')
            
            # Only update logo if a new one is provided
            if 'logo' in request.FILES:
                brand.logo = request.FILES['logo']
                
            brand.save()
            messages.success(request, f'Brand "{brand.name}" has been updated successfully')
            return redirect('admin_panel:brands')
            
        # Delete brand
        elif action == 'delete':
            brand_id = request.POST.get('brand_id')
            brand = get_object_or_404(Brand, id=brand_id)
            brand_name = brand.name
            brand.delete()
            
            messages.success(request, f'Brand "{brand_name}" has been deleted successfully')
            return redirect('admin_panel:brands')
    
    return render(request, 'admin_panel/brands/list.html', {'brands': brands})

@login_required
@user_passes_test(is_admin)
def brand_detail(request, brand_id):
    """Get brand details for editing"""
    try:
        brand = get_object_or_404(Brand, id=brand_id)
        
        # For AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            data = {
                'id': brand.id,
                'name': brand.name,
                'description': brand.description,
                'logo_url': brand.logo.url if brand.logo and brand.logo.name else None
            }
            return JsonResponse(data)
            
        # For regular requests
        return render(request, 'admin_panel/brands/detail.html', {'brand': brand})
    except Exception as e:
        # Log the error for debugging
        print(f"Error in brand_detail view: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        # Re-raise for regular requests
        raise