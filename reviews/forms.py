from django import forms
from .models import PropertyReview, LandlordReview

class PropertyReviewForm(forms.ModelForm):
    """Form for property reviews"""
    class Meta:
        model = PropertyReview
        fields = ['rating', 'cleanliness_rating', 'location_rating', 'value_rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'cleanliness_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'location_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'value_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this property...'})
        }

class LandlordReviewForm(forms.ModelForm):
    """Form for landlord reviews"""
    class Meta:
        model = LandlordReview
        fields = ['rating', 'communication_rating', 'responsiveness_rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'communication_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'responsiveness_rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this landlord...'})
        }