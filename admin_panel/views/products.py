from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product, Category, Brand

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_products(request):
    """View for managing products"""
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
                    stock=request.POST.get('stock')
                )
                
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                    product.save()
                
                messages.success(request, 'Product added successfully')
            except Exception as e:
                messages.error(request, f'Error creating product: {str(e)}')
                
        elif action == 'update':
            try:
                product = get_object_or_404(Product, id=request.POST.get('product_id'))
                product.name = request.POST.get('name')
                product.description = request.POST.get('description')
                product.price = request.POST.get('price')
                product.category_id = request.POST.get('category')
                product.brand_id = request.POST.get('brand')
                product.stock = request.POST.get('stock')
                
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                
                product.save()
                
                messages.success(request, 'Product updated successfully')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
                
        elif action == 'delete':
            try:
                product = get_object_or_404(Product, id=request.POST.get('product_id'))
                name = product.name
                product.delete()
                
                messages.success(request, 'Product deleted successfully')
                return redirect('admin_panel:products')
            except Exception as e:
                messages.error(request, f'Error deleting product: {str(e)}')
    
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    return render(request, 'admin_panel/products/list.html', {
        'products': products,
        'categories': categories,
        'brands': brands
    })

@login_required
@user_passes_test(is_admin)
def product_detail(request, product_id):
    """Get product details for editing"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            try:
                product.name = request.POST.get('name')
                product.description = request.POST.get('description')
                product.price = request.POST.get('price')
                product.category_id = request.POST.get('category')
                product.brand_id = request.POST.get('brand')
                product.stock = request.POST.get('stock')
                
                if 'image' in request.FILES:
                    product.image = request.FILES['image']
                
                product.save()
                messages.success(request, 'Product updated successfully')
                return redirect('admin_panel:products')
            except Exception as e:
                messages.error(request, f'Error updating product: {str(e)}')
        
        elif action == 'delete':
            try:
                name = product.name
                product.delete()
                messages.success(request, f'Product "{name}" deleted successfully')
                return redirect('admin_panel:products')
            except Exception as e:
                messages.error(request, f'Error deleting product: {str(e)}')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'category': product.category_id,
            'brand': product.brand_id,
            'stock': product.stock,
            'image_url': product.image.url if product.image else None
        }
        return JsonResponse(data)
    
    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'admin_panel/products/detail.html', {
        'product': product,
        'categories': categories,
        'brands': brands
    })