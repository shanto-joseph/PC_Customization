from django.db import models
from django.core.exceptions import ValidationError
from orders.models import Order
from customization.models import CustomPC

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('cod', 'Cash On Delivery')
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    custom_pc = models.ForeignKey('customization.CustomPC', on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_details = models.JSONField(null=True, blank=True)

    def __str__(self):
        if self.order:
            return f"Payment #{self.id} for Order #{self.order.id}"
        return f"Payment #{self.id} for Custom PC #{self.custom_pc.id}"

    def clean(self):
        """Ensure either order or custom_pc is set, but not both"""
        if self.order and self.custom_pc:
            raise ValidationError("Payment cannot be associated with both an order and a custom PC")
        if not self.order and not self.custom_pc:
            raise ValidationError("Payment must be associated with either an order or a custom PC")

    class Meta:
        ordering = ['-created_at']
