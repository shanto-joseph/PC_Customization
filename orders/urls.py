from django.urls import path
from . import views
from . import razorpay_views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.create_order, name='create_order'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('staff/', views.staff_orders, name='staff_orders'),
    # Razorpay routes
    path('razorpay/create/<int:order_id>/', razorpay_views.create_razorpay_order, name='create_razorpay_order'),
    path('razorpay/verify/<int:order_id>/', razorpay_views.verify_payment, name='verify_payment'),
]