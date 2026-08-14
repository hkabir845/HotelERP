"""User model."""
import bcrypt
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserRole(models.TextChoices):
    """Hotel job-function roles (least-privilege RBAC)."""

    SUPERADMIN = 'superadmin', 'Superadmin'
    ADMIN = 'admin', 'Admin'
    OPERATIONS_MANAGER = 'operations_manager', 'Operations Manager'
    MANAGER = 'manager', 'Manager'  # legacy alias → operations_manager
    FRONTDESK = 'frontdesk', 'Frontdesk'
    HOUSEKEEPING = 'housekeeping', 'Housekeeping'
    RESTAURANT = 'restaurant', 'Restaurant'
    FNB = 'fnb', 'F&B'  # legacy alias → restaurant
    ACCOUNTANT = 'accountant', 'Accountant'
    PURCHASE_OFFICER = 'purchase_officer', 'Purchase Officer'
    MAINTENANCE = 'maintenance', 'Maintenance'
    STAFF = 'staff', 'Staff'


class UserManager(BaseUserManager):
    """Custom user manager using bcrypt password hashing."""

    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.password = ''
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.SUPERADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model with bcrypt-compatible hashed_password column."""

    username = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.CharField(max_length=255, unique=True, db_index=True)
    password = models.CharField(max_length=255, db_column='hashed_password')
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.STAFF,
    )

    tenant = models.ForeignKey(
        'Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        db_index=True,
    )

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    avatar = models.CharField(max_length=500, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)

    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'

    @property
    def hashed_password(self):
        """Alias for FastAPI/SQLAlchemy compatibility."""
        return self.password

    @hashed_password.setter
    def hashed_password(self, value):
        self.password = value

    def set_password(self, raw_password):
        """Hash password with bcrypt (matches FastAPI app)."""
        if raw_password is None:
            self.password = ''
            return
        if isinstance(raw_password, str):
            raw_password = raw_password.encode('utf-8')
        if len(raw_password) > 72:
            raw_password = raw_password[:72]
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(raw_password, salt).decode('utf-8')

    def check_password(self, raw_password):
        """Verify password with bcrypt (matches FastAPI app)."""
        if not self.password:
            return False
        if isinstance(raw_password, str):
            raw_password = raw_password.encode('utf-8')
        hashed = self.password
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
        return bcrypt.checkpw(raw_password, hashed)

    def __str__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}')"
