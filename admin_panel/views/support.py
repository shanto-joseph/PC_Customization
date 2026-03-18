from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from support.models import SupportTicket, TicketResponse
from accounts.models import User
from notifications.models import Notification

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_support(request):
    """View for managing support tickets"""
    tickets = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/support/list.html', {'tickets': tickets})

@login_required
@user_passes_test(is_admin)
def ticket_detail(request, ticket_id):
    """View support ticket details"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    staff_members = User.objects.filter(role__name='staff')
    
    return render(request, 'admin_panel/support/detail.html', {
        'ticket': ticket,
        'staff_members': staff_members
    })

@login_required
@user_passes_test(is_admin)
def update_ticket_assignment(request, ticket_id):
    """Update ticket staff assignment"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        staff_id = request.POST.get('staff_id')
        
        if staff_id:
            try:
                staff = get_object_or_404(User, id=staff_id, role__name='staff')
                
                # Get current assigned staff before updating
                old_staff = None
                try:
                    if ticket.assigned_staff:
                        old_staff = ticket.assigned_staff
                except (User.DoesNotExist, AttributeError):
                    pass
                
                ticket.assigned_staff = staff
                ticket.save()
                
                # Notify new staff member
                Notification.create_notification(
                    user=staff,
                    type='ticket_assignment',
                    title='New Ticket Assignment',
                    message=f'You have been assigned to ticket #{ticket.id}',
                    link=f'/staff/support/{ticket.id}/'
                )
                
                # Notify old staff member if reassigned
                if old_staff and old_staff != staff:
                    Notification.create_notification(
                        user=old_staff,
                        type='ticket_assignment',
                        title='Ticket Reassigned',
                        message=f'Ticket #{ticket.id} has been reassigned to another staff member',
                        link=f'/staff/support/'
                    )
                
                messages.success(request, 'Staff member assigned successfully')
            except User.DoesNotExist:
                messages.error(request, 'Selected staff member not found')
        else:
            messages.error(request, 'No staff member selected')
        
    return redirect('admin_panel:ticket_detail', ticket_id=ticket_id)

@login_required
@user_passes_test(is_admin)
def respond_to_ticket(request, ticket_id):
    """Add response to support ticket"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        message = request.POST.get('message')
        if message:
            response = TicketResponse.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            
            # Notify customer
            Notification.create_notification(
                user=ticket.user,
                type='support',
                title='New Response on Your Ticket',
                message=f'Staff responded to your ticket #{ticket.id}',
                link=f'/support/ticket/{ticket.id}/'
            )
            
            messages.success(request, 'Response added successfully')
            
    return redirect('admin_panel:ticket_detail', ticket_id=ticket_id)

@login_required
@user_passes_test(is_admin)
def update_ticket_status(request, ticket_id):
    """Update support ticket status"""
    if request.method == 'POST':
        ticket = get_object_or_404(SupportTicket, id=ticket_id)
        old_status = ticket.status
        status = request.POST.get('status')
        
        ticket.status = status
        ticket.save()
        
        # Notify customer
        Notification.create_notification(
            user=ticket.user,
            type='support',
            title='Support Ticket Status Updated',
            message=f'Your ticket #{ticket.id} status has been updated to {status}',
            link=f'/support/ticket/{ticket.id}/'
        )
        
        # Notify assigned staff if any
        try:
            if ticket.assigned_staff:
                Notification.create_notification(
                    user=ticket.assigned_staff,
                    type='support',
                    title='Ticket Status Updated',
                    message=f'Ticket #{ticket.id} status has been updated to {status}',
                    link=f'/staff/support/{ticket.id}/'
                )
        except (User.DoesNotExist, AttributeError):
            pass
        
        messages.success(request, 'Ticket status updated successfully')
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
