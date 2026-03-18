from django.urls import path
from . import views

app_name = 'customization'

urlpatterns = [
    path('', views.custom_pc, name='custom_pc'),
    path('my-builds/', views.my_builds, name='my_builds'),
    path('build/<int:build_id>/', views.build_detail, name='build_detail'),
    path('build/<int:build_id>/pay/', views.proceed_to_payment, name='proceed_to_payment'),
    path('build/<int:build_id>/track/', views.track_build, name='track_build'),
    path('build/<int:build_id>/address/', views.update_shipping_address, name='update_shipping_address'),
    path('check-compatibility/', views.check_compatibility, name='check_compatibility'),
    path('staff/builds/', views.staff_builds, name='staff_builds'),
    path('staff/build/<int:build_id>/', views.staff_build_detail, name='staff_build_detail'),
]