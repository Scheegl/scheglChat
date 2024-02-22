from django.db import models
from django.contrib.auth.models import User
from easy_thumbnails.fields import ThumbnailerImageField


class Room(models.Model):
    name = models.CharField(max_length=16, unique=True)


class UserMod(models.Model):
    name = models.CharField(max_length=16, unique=True)
    room = models.OneToOneField(Room, on_delete=models.SET_NULL, null=True)
    # avatar = ThumbnailerImageField(resize_source={'size': (200, 200), 'crop': 'smart'}, upload_to='scheglChat',default='scheglChat/no_avatar.jpg')
    online = models.BooleanField(default=False)

    def user_list(self):
        users = UserMod.objects.filter().order_by('name')
        return list(users)


class Message(models.Model):
    text = models.CharField(max_length=256)
    author = models.ForeignKey(UserMod, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)