from rest_framework import serializers
from .models import UserMod, Room
from django.contrib.auth.models import User

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('id', 'name')


class UserModSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserMod
        fields = ('id','name','room')

