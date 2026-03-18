from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from products.models import Category

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_categories(request):
    """View for managing categories"""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            try:
                Category.objects.create(
                    name=request.POST.get('name'),
                    description=request.POST.get('description')
                )
                messages.success(request, 'Category added successfully')
            except Exception as e:
                messages.error(request, f'Error creating category: {str(e)}')
                
        elif action == 'update':
            try:
                category = get_object_or_404(Category, id=request.POST.get('category_id'))
                category.name = request.POST.get('name')
                category.description = request.POST.get('description')
                category.save()
                messages.success(request, 'Category updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
                
        elif action == 'delete':
            try:
                category = get_object_or_404(Category, id=request.POST.get('category_id'))
                category.delete()
                messages.success(request, 'Category deleted successfully')
            except Exception as e:
                messages.error(request, f'Error deleting category: {str(e)}')
    
    categories = Category.objects.all()
    return render(request, 'admin_panel/categories/list.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def category_detail(request, category_id):
    """Get category details for editing"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': category.id,
            'name': category.name,
            'description': category.description
        }
        return JsonResponse(data)
    
    return render(request, 'admin_panel/categories/detail.html', {'category': category})