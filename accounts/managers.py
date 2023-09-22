from django.db import models
from django.contrib.auth.base_user import BaseUserManager

class MyUserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self,username,email,password,phone):

        if not username:
            raise ValueError('Users must have username')
        
        if not email:
            raise ValueError('Users must have email')

        email = self.normalize_email(email)

        user = self.model(
            username = username,
            email = email,
            password=password,
            phone = phone,
        )
        # user.is_superuser= True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password,phone):
        
        user = self.create_user(
            username,
            email,
            password,
            phone,
        )
        user.is_staff = True
        user.is_verified = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


