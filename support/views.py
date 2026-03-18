from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SupportTicket, TicketResponse
from orders.models import Order
from notifications.models import Notification

def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if request.user.is_authenticated:
            ticket = SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                message=message
            )
            messages.success(request, 'Your message has been sent. We will get back to you soon.')
            return redirect('support:ticket_detail', ticket_id=ticket.id)
        else:
            messages.info(request, 'Please login to submit a support ticket.')
            return redirect('accounts:login')
    
    return render(request, 'support/contact.html')

@login_required
def ticket_list(request):
    """Display user's support tickets"""
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'support/ticket_list.html', {'tickets': tickets})

@login_required
def create_ticket(request):
    """Create a new support ticket"""
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        order_id = request.POST.get('order_id')
        
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject,
            message=message
        )
        
        if order_id:
            order = get_object_or_404(Order, id=order_id, user=request.user)
            ticket.order = order
            ticket.save()
        
        # Notify staff
        staff_users = User.objects.filter(role__name='staff')
        for staff in staff_users:
            Notification.create_notification(
                user=staff,
                type='support',
                title='New Support Ticket',
                message=f'A new support ticket has been created: {subject}',
                link=f'/support/staff/ticket/{ticket.id}/'
            )
        
        messages.success(request, 'Support ticket created successfully')
        return redirect('support:ticket_detail', ticket_id=ticket.id)
    
    # Check if there's an order reference
    order_id = request.GET.get('order')
    order = None
    if order_id:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    
    return render(request, 'support/create_ticket.html', {'order': order})

@login_required
def ticket_detail(request, ticket_id):
    """Display ticket details and handle responses"""
    ticket = get_object_or_404(SupportTicket, id=ticket_id, user=request.user)
    
    if request.method == 'POST':
        message = request.POST.get('response')
        if message:
            TicketResponse.objects.create(
                ticket=ticket,
                user=request.user,
                message=message
            )
            
            # Notify staff
            if ticket.assigned_staff:
                Notification.create_notification(
                    user=ticket.assigned_staff,
                    type='support',
                    title='New Response on Support Ticket',
                    message=f'Customer responded to ticket #{ticket.id}',
                    link=f'/support/staff/ticket/{ticket.id}/'
                )
            
            messages.success(request, 'Response added successfully')
            return redirect('support:ticket_detail', ticket_id=ticket.id)
    
    return render(request, 'support/ticket_detail.html', {'ticket': ticket})

@login_required
def staff_tickets(request):
    """Staff view for managing support tickets"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    tickets = SupportTicket.objects.all().order_by('-created_at')
    return render(request, 'staff_panel/support/list.html', {'tickets': tickets})

@login_required
def staff_ticket_detail(request, ticket_id):
    """Staff view for ticket details"""
    if not request.user.is_staff_member:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign':
            ticket.assigned_staff = request.user
            ticket.status = 'in_progress'
            ticket.save()
            
            # Notify customer
            Notification.create_notification(
                user=ticket.user,
                type='support',
                title='Support Ticket Updated',
                message=f'Your ticket has been assigned to {request.user.get_full_name()}',
                link=f'/support/ticket/{ticket.id}/'
            )
            
            messages.success(request, 'Ticket assigned successfully')
            
        elif action == 'respond':
            message = request.POST.get('response')
            if message:
                TicketResponse.objects.create(
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
                
        elif action == 'close':
            ticket.status = 'closed'
            ticket.save()
            
            # Notify customer
            Notification.create_notification(
                user=ticket.user,
                type='support',
                title='Support Ticket Closed',
                message=f'Your ticket #{ticket.id} has been closed',
                link=f'/support/ticket/{ticket.id}/'
            )
            
            messages.success(request, 'Ticket closed successfully')
    
    return render(request, 'staff_panel/support/detail.html', {'ticket': ticket})