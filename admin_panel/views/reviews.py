from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from reviews.models import ProductReview

def is_admin(user):
    return user.is_authenticated and user.is_admin

@login_required
@user_passes_test(is_admin)
def manage_reviews(request):
    """View for managing product reviews"""
    
    # Handle the delete action
    if request.method == 'POST' and request.POST.get('action') == 'delete':
        review_id = request.POST.get('review_id')
        try:
            review = ProductReview.objects.get(id=review_id)
            review.delete()
            messages.success(request, 'Review deleted successfully.')
        except ProductReview.DoesNotExist:
            messages.error(request, 'Review not found.')
        return redirect('/admin/reviews/')  # Direct URL path instead of named URL
    
    # Get all reviews for display
    reviews = ProductReview.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/reviews/list.html', {'reviews': reviews})
