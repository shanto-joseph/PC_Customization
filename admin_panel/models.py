from django.db import models
from accounts.models import User

class StoreAnalytics(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    total_custom_builds = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Store Analytics'
    
    def __str__(self):
        return f"Analytics for {self.date}"