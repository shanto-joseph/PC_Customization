from django.db import models
from accounts.models import User, ShippingAddress
from products.models import Product

class CustomPC(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Payment Pending'),
        ('rejected', 'Rejected'),
        ('paid', 'Payment Received'),
        ('in_progress', 'In Progress'),
        ('assembling', 'Assembly in Progress'),
        ('testing', 'Testing'),
        ('shipping', 'Shipping'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    cpu = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_cpu', null=True)
    motherboard = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_motherboard', null=True)
    ram = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_ram', null=True)
    gpu = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_gpu', null=True)
    storage = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_storage', null=True)
    case = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_case', null=True)
    power_supply = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='custom_pc_power_supply', null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    assembly_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_custom_builds')
    rejection_reason = models.TextField(blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Custom PC - {self.name}"
    
    @property
    def get_components_total(self):
        """Calculate total price of all components without service charge"""
        total = 0
        components = [self.cpu, self.motherboard, self.ram, self.gpu, self.storage, self.case, self.power_supply]
        for component in components:
            if component:
                total += component.price
        return total

    @property
    def get_total_price(self):
        """Calculate total price including service charge"""
        return self.get_components_total + self.service_charge

    def is_complete(self):
        """Check if all required components are selected"""
        return all([self.cpu, self.motherboard, self.ram, self.gpu, 
                   self.storage, self.case, self.power_supply])

    def validate_compatibility(self):
        """
        Validate component compatibility
        Returns (is_compatible, error_message)
        """
        if not self.is_complete():
            return False, "All components must be selected"
            
        # Check CPU and Motherboard compatibility
        if self.cpu and self.motherboard:
            if self.cpu.category.name == 'Intel' and 'AMD' in self.motherboard.name:
                return False, "Intel CPU is not compatible with AMD motherboard"
            if self.cpu.category.name == 'AMD' and 'Intel' in self.motherboard.name:
                return False, "AMD CPU is not compatible with Intel motherboard"
        
        # Add more compatibility checks as needed
        return True, "All components are compatible"

    @property
    def needs_payment(self):
        """Check if build needs payment"""
        return self.status == 'approved'

    @property
    def is_paid(self):
        """Check if build is paid"""
        return self.status in ['paid', 'in_progress', 'assembling', 'testing', 'shipping', 'delivered']