from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse
from .models import User, Role, ShippingAddress
from customization.models import CustomPC

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_customer:
                    login(request, user)
                    return redirect('products:home')
                elif user.is_admin:
                    messages.error(request, 'Please use the admin login page')
                    return redirect('accounts:admin_login')
                elif user.is_staff_member:
                    messages.error(request, 'Please use the staff login page')
                    return redirect('accounts:staff_login')
            else:
                messages.error(request, 'Invalid credentials')
        except Exception as e:
            messages.error(request, 'An error occurred during login')
    
    return render(request, 'authentication/login.html')

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_admin:
                    login(request, user)
                    return redirect('admin_panel:dashboard')
                elif user.is_customer:
                    messages.error(request, 'Please use the customer login page')
                    return redirect('accounts:login')
                elif user.is_staff_member:
                    messages.error(request, 'Please use the staff login page')
                    return redirect('accounts:staff_login')
            else:
                messages.error(request, 'Invalid admin credentials')
        except Exception as e:
            messages.error(request, 'An error occurred during login')
    
    return render(request, 'authentication/admin_login.html')

def staff_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, email=email, password=password)
            if user is not None:
                if user.is_staff_member:
                    login(request, user)
                    return redirect('accounts:staff_dashboard')
                elif user.is_admin:
                    messages.error(request, 'Please use the admin login page')
                    return redirect('accounts:admin_login')
                elif user.is_customer:
                    messages.error(request, 'Please use the customer login page')
                    return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid staff credentials')
        except Exception as e:
            messages.error(request, 'An error occurred during login')
    
    return render(request, 'authentication/staff_login.html')

def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        profile_image = request.FILES.get('profile_image')
        
        try:
            # Get or create customer role
            customer_role, created = Role.objects.get_or_create(name='customer')
            
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                role=customer_role,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                profile_image=profile_image
            )
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('products:home')
            
        except Exception as e:
            messages.error(request, 'An error occurred during registration')
    
    return render(request, 'authentication/register.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_staff': User.objects.filter(role__name='staff').count(),
        'total_customers': User.objects.filter(role__name='customer').count(),
        'total_builds': CustomPC.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff_member)
def staff_dashboard(request):
    context = {
        'pending_builds': CustomPC.objects.filter(status='pending').count(),
        'assigned_builds': CustomPC.objects.filter(assigned_staff=request.user).count(),
        'recent_builds': CustomPC.objects.filter(assigned_staff=request.user).order_by('-created_at')[:5],
    }
    return render(request, 'staff_panel/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'authentication/profile.html')

@login_required
@user_passes_test(lambda u: u.is_admin)
def admin_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:admin_profile')
    
    return render(request, 'authentication/profile.html')

@login_required
@user_passes_test(lambda u: u.is_staff_member)
def staff_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:staff_profile')
    
    return render(request, 'authentication/profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'authentication/change_password.html', {'form': form})

@login_required
def add_address(request):
    """Add a new shipping address"""
    if request.method == 'POST':
        # Convert checkbox value to boolean
        is_default = request.POST.get('is_default') == 'on'
        
        address = ShippingAddress.objects.create(
            user=request.user,
            address_line1=request.POST.get('address_line1'),
            address_line2=request.POST.get('address_line2'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country'),
            is_default=is_default
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
            
        messages.success(request, 'Address added successfully!')
        return redirect('accounts:profile')
    return redirect('accounts:profile')

@login_required
def get_address(request, address_id):
    """Get address details for editing"""
    address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': address.id,
            'address_line1': address.address_line1,
            'address_line2': address.address_line2 or '',
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'country': address.country,
            'is_default': address.is_default
        }
        return JsonResponse(data)
    return redirect('accounts:profile')

@login_required
def update_address(request, address_id):
    """Update shipping address"""
    if request.method == 'POST':
        address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
        address.address_line1 = request.POST.get('address_line1')
        address.address_line2 = request.POST.get('address_line2')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.postal_code = request.POST.get('postal_code')
        address.country = request.POST.get('country')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        messages.success(request, 'Address updated successfully!')
        return redirect('accounts:profile')
    return redirect('accounts:profile')

@login_required
def delete_address(request, address_id):
    if request.method == 'POST':
        address = get_object_or_404(ShippingAddress, id=address_id, user=request.user)
        if not address.is_default:
            address.delete()
            messages.success(request, 'Address deleted successfully!')
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'Cannot delete default address'})
    return JsonResponse({'success': False}, status=405)