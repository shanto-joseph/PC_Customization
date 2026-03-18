from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django's built-in admin
    path('admin/', include('admin_panel.urls')),  # Custom admin panel
    path('staff/', include('staff_panel.urls')),  # Staff panel
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('customization/', include('customization.urls')),
    path('support/', include('support.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('notifications/', include('notifications.urls')),
    path('reviews/', include('reviews.urls')),  # Add reviews URLs
    path('chatbot/', include('chatbot.urls')),  # Vex AI Chatbot
    # Change this line to avoid namespace conflict
    path('', include('products.urls', namespace='products')),  # Root URL patterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)