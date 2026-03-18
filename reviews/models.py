from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User
from products.models import Product

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customer_reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_reviews_authored')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'product')  # One review per user per product
    
    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"