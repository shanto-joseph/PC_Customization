from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.ticket_list, name='ticket_list'),
    path('contact/', views.contact, name='contact'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('staff/tickets/', views.staff_tickets, name='staff_tickets'),
    path('staff/ticket/<int:ticket_id>/', views.staff_ticket_detail, name='staff_ticket_detail'),
]