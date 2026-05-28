from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required!")
        email = self.normalize_email(email)
        # creating the object
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email=email, name=name, password=password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    college_name = models.CharField(max_length=200, blank=True, null=True)
    register_no = models.CharField(max_length=50, blank=True, null=True)
    class_section = models.CharField(max_length=30, blank=True, null=True)
    college_email = models.EmailField(unique=True, blank=True, null=True)

#Google auth fields
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    auth_provider = models.CharField(
        max_length=20, 
        choices=[('email', 'Email'), ('google', 'Google')],
        default='email')
    profile_complete = models.BooleanField(default=False)

    #college email verification
    college_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"