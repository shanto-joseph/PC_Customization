from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from admin_panel.models import ActivityLog

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def activity_logs(request):
    """View activity logs"""
    logs = ActivityLog.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/logs/list.html', {'logs': logs})