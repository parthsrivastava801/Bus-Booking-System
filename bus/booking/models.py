from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('passenger', 'Passenger'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='passenger')
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def is_passenger(self):
        return self.user_type == 'passenger'

    def is_admin(self):
        return self.user_type == 'admin'
