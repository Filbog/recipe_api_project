from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    # extra_fields is basically any other fields we provide, like is_active and/or any
    # new in the future
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user


# AbstractBaseUser contains the functionality for the auth system but not any fields,
# PermissionsMixin for permissions and fields necessary for the permissions feature
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # this is basically how we assign UserManager
    objects = UserManager()

    # default User Model uses 'username' property, ours doesnt have this (for purpose) and we use email
    USERNAME_FIELD = "email"
