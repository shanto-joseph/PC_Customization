from django.urls import reverse

def user_roles(request):
    """
    Context processor to add role-based information to all templates
    """
    context = {
        'is_admin_panel': False,
        'is_staff_panel': False,
        'panel_name': None,
        'panel_urls': {},
    }
    
    if not request.user.is_authenticated:
        return context
        
    # Set panel context based on user role and current URL
    if request.user.is_admin:
        context['is_admin_panel'] = request.path.startswith('/admin/')
        context['panel_name'] = 'Admin Panel'
        context['panel_urls'] = {
            'dashboard': reverse('admin_panel:dashboard'),
            'users': reverse('admin_panel:users'),
            'products': reverse('admin_panel:products'),
            'orders': reverse('admin_panel:orders'),
            'custom_builds': reverse('admin_panel:custom_builds'),
            'analytics': reverse('admin_panel:analytics'),
            'profile': reverse('admin_panel:profile'),
        }
    elif request.user.is_staff_member:
        context['is_staff_panel'] = request.path.startswith('/staff/')
        context['panel_name'] = 'Staff Panel'
        context['panel_urls'] = {
            'dashboard': reverse('staff_panel:dashboard'),
            'products': reverse('staff_panel:products'),
            'orders': reverse('staff_panel:orders'),
            'builds': reverse('customization:staff_builds'),
            'support_tickets': reverse('support:staff_tickets'),
            'profile': reverse('accounts:staff_profile'),
        }
    
    return context