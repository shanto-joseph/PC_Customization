from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        # Automatically assign the 'admin' role for superusers.
        admin_role, created = Role.objects.get_or_create(name='admin')
        extra_fields.setdefault('role', admin_role)
        user = self.create_user(email, username, password, **extra_fields)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=191)
    password = models.CharField(max_length=128)  # Django handles password hashing
    username = models.CharField(max_length=150, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='role_id')
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        """
        Computes staff status based on the role.
        Users with role 'admin' or 'staff' are treated as staff.
        """
        return self.role.name.lower() in ['admin', 'staff']

    @property
    def is_superuser(self):
        """
        Computes superuser status based solely on the role.
        Only users with role 'admin' are considered superusers.
        """
        return self.role.name.lower() == 'admin'

    def has_perm(self, perm, obj=None):
        """
        Check if the user has a specific permission.
        Admins have all permissions, staff have limited permissions.
        """
        if self.is_admin:
            return True
        elif self.is_staff_member:
            # Define specific permissions for staff members
            staff_permissions = [
                'view_product',
                'change_product',
                'view_order',
                'change_order',
                'view_custompc',
                'change_custompc',
                'view_supportticket',
                'change_supportticket'
            ]
            return perm in staff_permissions
        return False

    def has_module_perms(self, app_label):
        """
        Check if the user has permissions to view the app `app_label`.
        Admins can view all modules, staff can view specific modules.
        """
        if self.is_admin:
            return True
        elif self.is_staff_member:
            # Define which apps staff members can access
            staff_apps = ['products', 'orders', 'customization', 'support']
            return app_label in staff_apps
        return False

    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role.name.lower() == 'admin'
    
    @property
    def is_customer(self):
        """Check if user has customer role"""
        return self.role.name.lower() == 'customer'
    
    @property
    def is_staff_member(self):
        """Check if user has staff role"""
        return self.role.name.lower() == 'staff'

    def get_full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the short name of the user"""
        return self.first_name

class ShippingAddress(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s address - {self.address_line1}"
    
    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses of this user to non-default
            ShippingAddress.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)