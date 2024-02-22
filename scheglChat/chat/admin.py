from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserMod, Room, Message

admin.site.register(UserMod)
admin.site.register(Room)
admin.site.register(Message)
