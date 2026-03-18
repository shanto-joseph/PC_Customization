from django.urls import path
from . import views
from . import razorpay_views

app_name = 'cart'

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('prepare-checkout/', views.prepare_checkout, name='prepare_checkout'),
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    # Razorpay
    path('razorpay/create/', razorpay_views.create_razorpay_order, name='create_razorpay_order'),
    path('razorpay/verify/', razorpay_views.verify_razorpay_payment, name='verify_razorpay_payment'),
    path('dummy-payment/', razorpay_views.process_dummy_payment, name='process_dummy_payment'),
]