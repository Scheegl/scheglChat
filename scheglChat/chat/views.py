from django.shortcuts import render
from django.http import JsonResponse
from .models import UserMod, Room
from .serializer import RoomSerializer, UserModSerializer
from rest_framework.viewsets import ModelViewSet


def api_users(request):
    if request.method == 'GET':
        users = UserMod.objects.all()
        serializer = UserModSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)


class ApiUsers(ModelViewSet):
    queryset = UserMod.objects.all()
    serializer_class = UserModSerializer

class ApiRooms(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

