from django.db import models
from accounts.models import User
from products.models import Product, Discount

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s cart"
    
    @property
    def get_subtotal(self):
        """Get cart subtotal before discount"""
        cart_items = self.cartitem_set.all()
        return sum([item.get_total for item in cart_items])
    
    @property
    def get_discount_amount(self):
        """Get discount amount if coupon is applied"""
        if not self.coupon:
            return 0
        
        subtotal = self.get_subtotal
        if self.coupon.discount_type == 'percentage':
            return subtotal * (self.coupon.discount_value / 100)
        else:
            return min(self.coupon.discount_value, subtotal)  # Don't allow negative totals
    
    @property
    def get_cart_total(self):
        """Get final cart total after discount"""
        return max(self.get_subtotal - self.get_discount_amount, 0)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def get_total(self):
        return self.product.price * self.quantity