from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and not request.path.startswith('/admin/login'):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access admin panel.')
                return redirect('accounts:admin_login')
            elif not request.user.is_admin:
                messages.error(request, 'You do not have permission to access admin panel.')
                return redirect('accounts:login')
        
        response = self.get_response(request)
        return response