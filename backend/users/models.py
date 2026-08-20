from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Maps to the SRS's "Users" table:
    User_ID (id, auto) · Name (first_name/last_name) · Email · Password · Role
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        FACULTY = 'FACULTY', 'Faculty'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.FACULTY)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role})'

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_faculty_role(self):
        return self.role == self.Role.FACULTY
