from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from customization.models import CustomPC
from accounts.models import User
from notifications.models import Notification

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_custom_builds(request):
    """View for managing custom PC builds"""
    builds = CustomPC.objects.all().order_by('-created_at')
    staff_members = User.objects.filter(role__name='staff')
    return render(request, 'admin_panel/custom_builds/list.html', {
        'builds': builds,
        'staff_members': staff_members
    })

@login_required
@user_passes_test(is_admin)
def build_detail(request, build_id):
    """View custom PC build details"""
    build = get_object_or_404(CustomPC, id=build_id)
    staff_members = User.objects.filter(role__name='staff')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_staff':
            staff_id = request.POST.get('staff_id')
            if staff_id:
                staff = get_object_or_404(User, id=staff_id, role__name='staff')
                build.assigned_staff = staff
                build.save()
                
                # Notify staff
                Notification.create_notification(
                    user=staff,
                    type='build_assignment',
                    title='New Build Assignment',
                    message=f'You have been assigned to build #{build.id}. Please review and accept/reject.',
                    link=f'/staff/builds/{build.id}/'
                )
                
                messages.success(request, 'Staff member assigned successfully')
                return redirect('admin_panel:build_detail', build_id=build.id)
    
    return render(request, 'admin_panel/custom_builds/detail.html', {
        'build': build,
        'staff_members': staff_members
    })

@login_required
@user_passes_test(is_admin)
def update_build_status(request, build_id):
    """Update custom PC build status"""
    if request.method == 'POST':
        build = get_object_or_404(CustomPC, id=build_id)
        old_status = build.status
        status = request.POST.get('status')
        
        build.status = status
        if request.POST.get('assembly_notes'):
            build.assembly_notes = request.POST.get('assembly_notes')
        build.save()
        
        # Notify customer
        Notification.create_notification(
            user=build.user,
            type='build_status',
            title='Build Status Updated',
            message=f'Your custom PC build status has been updated to {status}',
            link=f'/customization/build/{build.id}/'
        )
        
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)