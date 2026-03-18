from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from .models import CustomPC
from products.models import Product
from accounts.models import ShippingAddress, User
from notifications.models import Notification
from payments.models import Payment
from datetime import timedelta, date

@login_required
def custom_pc(request):
    """Custom PC builder page"""
    if request.method == 'POST':
        # Get build name first
        build_name = request.POST.get('build_name')
        if not build_name:
            messages.error(request, 'Please provide a name for your build')
            return redirect('customization:custom_pc')
            
        # Get selected components
        cpu = request.POST.get('cpu')
        motherboard = request.POST.get('motherboard')
        ram = request.POST.get('ram')
        gpu = request.POST.get('gpu')
        storage = request.POST.get('storage')
        case = request.POST.get('case')
        power_supply = request.POST.get('power_supply')
        
        # Validate all components are selected
        if not all([cpu, motherboard, ram, gpu, storage, case, power_supply]):
            messages.error(request, 'Please select all components')
            return redirect('customization:custom_pc')
        
        try:
            # Create custom PC build
            build = CustomPC.objects.create(
                user=request.user,
                name=build_name,
                cpu_id=cpu,
                motherboard_id=motherboard,
                ram_id=ram,
                gpu_id=gpu,
                storage_id=storage,
                case_id=case,
                power_supply_id=power_supply,
                status='pending'
            )
            
            # Notify admin
            admin_users = User.objects.filter(role__name='admin')
            for admin in admin_users:
                Notification.create_notification(
                    user=admin,
                    type='build_approval',
                    title='New Custom PC Build',
                    message=f'A new custom PC build requires approval: {build_name}',
                    link=f'/admin/custom-builds/{build.id}/'
                )
            
            messages.success(request, 'Your custom PC build has been submitted for review')
            return redirect('customization:build_detail', build_id=build.id)
            
        except Exception as e:
            messages.error(request, f'Error creating build: {str(e)}')
            return redirect('customization:custom_pc')
    
    # Get components for selection
    context = {
        'cpus': Product.objects.filter(category__name='CPU'),
        'motherboards': Product.objects.filter(category__name='Motherboard'),
        'rams': Product.objects.filter(category__name='RAM'),
        'gpus': Product.objects.filter(category__name='GPU'),
        'storages': Product.objects.filter(category__name='Storage'),
        'cases': Product.objects.filter(category__name='Case'),
        'power_supplies': Product.objects.filter(category__name='PSU')
    }
    return render(request, 'customization/custom_pc.html', context)

@login_required
def my_builds(request):
    """Display user's custom PC builds"""
    builds = CustomPC.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customization/my_builds.html', {'builds': builds})

@login_required
def build_detail(request, build_id):
    """Display custom PC build details"""
    build = get_object_or_404(CustomPC, id=build_id, user=request.user)
    
    # Always show build details - let user decide when to proceed to payment
    return render(request, 'customization/build_detail.html', {'build': build})

@login_required
def proceed_to_payment(request, build_id):
    """Handle shipping address selection and proceed to payment"""
    build = get_object_or_404(CustomPC, id=build_id, user=request.user)
    
    # Check if build is approved
    if build.status != 'approved':
        messages.error(request, 'Build must be approved before payment')
        return redirect('customization:build_detail', build_id=build.id)
    
    # If no shipping address, show address selection
    if not build.shipping_address:
        addresses = request.user.shippingaddress_set.all()
        return render(request, 'customization/shipping_address.html', {
            'build': build,
            'addresses': addresses
        })
    
    # If shipping address exists, proceed to payment
    return redirect('payments:process_payment', payment_type='custom_pc', object_id=build.id)


@login_required
def update_shipping_address(request, build_id):
    """Update shipping address for custom PC build"""
    build = get_object_or_404(CustomPC, id=build_id, user=request.user)
    
    if request.method == 'POST':
        address_id = request.POST.get('shipping_address_id')
        if address_id:
            build.shipping_address_id = address_id
            build.save()
            messages.success(request, 'Shipping address updated successfully')
            return redirect('payments:process_payment', payment_type='custom_pc', object_id=build.id)
        else:
            messages.error(request, 'Please select a shipping address')
    
    return redirect('customization:build_detail', build_id=build_id)

@login_required
def check_compatibility(request):
    """Check component compatibility"""
    if request.method == 'POST':
        cpu_id = request.POST.get('cpu')
        motherboard_id = request.POST.get('motherboard')
        
        cpu = get_object_or_404(Product, id=cpu_id)
        motherboard = get_object_or_404(Product, id=motherboard_id)
        
        # Basic compatibility check
        is_compatible = True
        message = "Components are compatible"
        
        if 'Intel' in cpu.name and 'AMD' in motherboard.name:
            is_compatible = False
            message = "Intel CPU is not compatible with AMD motherboard"
        elif 'AMD' in cpu.name and 'Intel' in motherboard.name:
            is_compatible = False
            message = "AMD CPU is not compatible with Intel motherboard"
        
        return JsonResponse({
            'compatible': is_compatible,
            'message': message
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def track_build(request, build_id):
    """Track custom PC build status"""
    build = get_object_or_404(CustomPC, id=build_id, user=request.user)
    return render(request, 'customization/track_build.html', {'build': build})

@login_required
def staff_builds(request):
    """Staff view for managing custom PC builds"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    builds = CustomPC.objects.all().order_by('-created_at')
    return render(request, 'staff_panel/builds/list.html', {'builds': builds})

@login_required
def staff_build_detail(request, build_id):
    """Staff view for build details"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('products:home')  # Updated to use the correct URL name
    
    build = get_object_or_404(CustomPC, id=build_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            status = request.POST.get('status')
            rejection_reason = request.POST.get('rejection_reason')
            assembly_notes = request.POST.get('assembly_notes')

            if not status:
                return JsonResponse({
                    'success': False,
                    'message': 'Status cannot be empty'
                }, status=400)

            build.status = status
            
            if status == 'rejected' and rejection_reason:
                build.rejection_reason = rejection_reason
                build.assembly_notes = rejection_reason
            elif assembly_notes:
                build.assembly_notes = assembly_notes
            
            build.save()
            
            # Notify customer
            notification_message = f'Your custom PC build status has been updated to {build.get_status_display()}'
            if status == 'rejected' and rejection_reason:
                notification_message = f'Your custom PC build has been rejected. Reason: {rejection_reason}'
            
            Notification.create_notification(
                user=build.user,
                type='build_status',
                title='Build Status Updated',
                message=notification_message,
                link=f'/customization/build/{build.id}/'
            )
            
            messages.success(request, 'Build status updated successfully')
            return redirect('customization:staff_build_detail', build_id=build.id)
            
        elif action == 'assign':
            build.assigned_staff = request.user
            build.status = 'in_progress'
            build.save()
            
            messages.success(request, 'Build assigned successfully')
    
    return render(request, 'staff_panel/builds/detail.html', {'build': build})


