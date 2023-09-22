import uuid
from django.db import models
from .user_model import Users


class Images(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    path = models.ImageField(unique=True)
    format = models.CharField(max_length=100)


class ImagesAdmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    path = models.ImageField(unique=True)
    format = models.CharField(max_length=100)


class LinksAdmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image_id = models.CharField(max_length=100)
    expiration_time = models.IntegerField()
