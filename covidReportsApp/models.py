from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from covidReportsApp.manager import UserManager


class UserRegistration(AbstractUser):
    name = models.CharField(max_length=255)
    username = models.CharField(primary_key=True, max_length=128)
    password = models.CharField(max_length=256)
    mobile = models.BigIntegerField()
    email = models.EmailField()
    added_date = models.DateTimeField(auto_now_add=datetime.now())

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "user_register"
        constraints = [models.UniqueConstraint(fields=['username', 'mobile'], name="user_register_uniq")]

class CovidReportByUser(models.Model):
    username = models.CharField(primary_key=True, max_length=128)
    countries_handled_by_user = models.TextField(max_length=1000)
    added_date = models.DateTimeField(auto_now_add=datetime.now())
    updated_date = models.DateTimeField(auto_now=datetime.now())

    class Meta:
        db_table = "country_by_user"
        constraints = [models.UniqueConstraint(fields=['username'], name="country_by_user_uniq")]
