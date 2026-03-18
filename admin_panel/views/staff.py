from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import User, Role

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_staff(request):
    """View for managing staff members"""
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            # Get form data
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name', '')
            last_name = request.POST.get('last_name', '')
            phone_number = request.POST.get('phone_number', '')
            
            try:
                # Get staff role
                staff_role = Role.objects.get(name='staff')
                
                # Create new staff user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=phone_number,
                    role=staff_role
                )
                messages.success(request, f'Staff member {user.get_full_name() or user.username} has been added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding staff member: {str(e)}')
            
            return redirect('admin_panel:staff')
        
        elif action == 'update':
            # Handle update action
            staff_id = request.POST.get('staff_id')
            staff = get_object_or_404(User, id=staff_id)
            
            try:
                staff.email = request.POST.get('email')
                staff.first_name = request.POST.get('first_name', '')
                staff.last_name = request.POST.get('last_name', '')
                staff.phone_number = request.POST.get('phone_number', '')
                staff.is_active = 'is_active' in request.POST
                
                staff.save()
                messages.success(request, f'Staff member {staff.get_full_name() or staff.username} has been updated.')
            except Exception as e:
                messages.error(request, f'Error updating staff member: {str(e)}')
            
            return redirect('admin_panel:staff')
            
        elif action == 'delete':
            # Handle delete action
            staff_id = request.POST.get('staff_id')
            
            try:
                # Get staff member
                staff = get_object_or_404(User, id=staff_id)
                staff_name = staff.get_full_name() or staff.username
                
                # Safely delete the staff member
                # Instead of a hard delete that might trigger dependencies,
                # we'll mark as inactive and set a special flag
                staff.is_active = False
                staff.save()
                
                messages.success(request, f'Staff member {staff_name} has been deactivated.')
            except Exception as e:
                messages.error(request, f'Error deleting staff member: {str(e)}')
            
            return redirect('admin_panel:staff')
    
    # Get all staff members for display
    staff_members = User.objects.filter(role__name='staff')
    return render(request, 'admin_panel/staff/list.html', {'staff_members': staff_members})

@login_required
@user_passes_test(is_admin)
def staff_detail(request, staff_id):
    """View staff member details or return JSON for AJAX requests"""
    staff = get_object_or_404(User, id=staff_id)
    
    # If it's an AJAX request, return JSON data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'id': staff.id,
            'email': staff.email,
            'username': staff.username,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'phone_number': staff.phone_number or '',
            'is_active': staff.is_active
        }
        return JsonResponse(data)
    
    # If it's a regular GET request, redirect to staff list
    # since we don't have a detail template
    return HttpResponseRedirect(reverse('admin_panel:staff'))