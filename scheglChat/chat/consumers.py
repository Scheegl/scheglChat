import json
from .models import UserMod, Room, Message
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


def userlist():
    objects = UserMod.objects.filter().order_by('-name')
    list = {'UserList': 'UserList'}
    for object in objects:
        list[object.id] = object.name
    return list

def roomlist():
    objects = Room.objects.filter()
    list = {'RoomList': 'RoomList'}
    for object in objects:
        list[object.id] = object.name
    return list

def messagelist(id):
    objects = Message.objects.filter(room_id=id)
    name = Room.objects.get(id=id).name
    list = {'MessageList': name}
    for object in objects:
        message = {object.author.name: object.text}
        list[object.id] = message
    return list


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(json.dumps({'message': 'Connected'}))
        async_to_sync(self.channel_layer.group_add)("all_instructions", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("all_instructions", self.channel_name)

    def all_user(self, text_data=None):
        message = text_data
        print('order for all users:', message)
        if message['order'] == "send_list_users":
            self.send(json.dumps(userlist()))
            print('New users list sent to all users')
        if message['order'] == "send_list_rooms":
            self.send(json.dumps(roomlist()))
            print('New room list sent to all users')

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        print('incoming path:', self.scope["path"])
        print('incoming instructions message:', message)

        if 'load' in message:
            if message['load'] == "users":
                self.send(json.dumps(userlist()))
                print('Userlist sent to client')
            if message['load'] == 'rooms':
                self.send(json.dumps(roomlist()))
                print('Roomlist sent to client')
            if message['load'] == 'messageList':
                self.send(json.dumps(messagelist(message['newroom_id'])))
                print('Message List from ID room:', message['newroom_id'], 'sent to client')

        if 'create_user' in message:
            name = message['create_user']
            if not UserMod.objects.filter(name=name).exists():
                user = UserMod(name=name)
                user.save()
                print('New user', name, 'create')
                async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_users"})
            else:
                self.send(json.dumps({"message":"User with same name already exist"}))
                print("This user is already exist")

        if 'create_room' in message:
            name = message['create_room']
            if not Room.objects.filter(name=name).exists():
                room = Room(name=name)
                room.save()
                print('New room', name, 'create')
                async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})
            else:
                self.send(json.dumps({"message":"Room with same name already exist"}))
                print("This room already exist")

        if 'delete_user' in message:
            id = message['delete_user']
            user = UserMod.objects.get(id=id)
            user.delete()
            print('User ID', id, 'delete')
            async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_users"})

        if 'delete_room' in message:
            id = message['delete_room']
            room = Room.objects.get(id=id)
            room.delete()
            print('Room ID', id, 'delete')
            async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})

        if 'order' in message:
            if message['order'] == 'changeUserName':
                id = message['id']
                name = message['name']
                if not UserMod.objects.filter(name=name).exists():
                    user = UserMod.objects.get(id=id)
                    user.name = name
                    user.save()
                    print('Name user ID', id, 'change to', name)
                    async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_users"})
                else:
                    self.send((json.dumps({'message': 'This user is already exists'})))
                    print('This user is already exists')

            if message['order'] == 'changeRoomName':
                id = message['id']
                name = message['name']
                if not Room.objects.filter(name=name).exists():
                    room = Room.objects.get(id=id)
                    room.name = name
                    room.save()
                    print('Room name ID', id, 'change to', name)
                    async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})
                else:
                    self.send((json.dumps({'message': 'This room is already exists'})))
                    print('This room is already exists')


class WSChat(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(json.dumps({'message': 'Connected'}))
        async_to_sync(self.channel_layer.group_add)("all_chat", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("all_chat", self.channel_name)

    def incoming_message(self, text_data=None):
        message = text_data
        print('incoming message from group:', message)
        if message['order'] == "accept_message":
            name = message['name']
            message = message['message']
            self.send(json.dumps({'message': message, 'name': name}))
            print('Message recived by client')

    def all_chats(self, text_data=None):
        message = text_data
        print('incoming message from group:', message)

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        print('incoming path:', self.scope["path"])
        print('incoming instructions message:', message)

        # if 'usersendcommandroom' in message:
        #     if message['usersendcommandroom'] == 'roomselect':
        #         oldroom_id = str(message['oldroom_id'])
        #         async_to_sync(self.channel_layer.group_discard)(oldroom_id, self.channel_name)
        #         print('Disconnected from room', oldroom_id)
        #     newroom_id = str(message['newroom_id'])
        #     async_to_sync(self.channel_layer.group_add)(newroom_id, self.channel_name)
        #     print('Connected to room', newroom_id)

        if 'usersendcommandroom' in message:
            if message['usersendcommandroom'] == 'roomselect':
                if 'oldroom_id' in message:
                    oldroom_id = str(message['oldroom_id'])
                    async_to_sync(self.channel_layer.group_discard)(oldroom_id, self.channel_name)
                    print('Disconnected from room', oldroom_id)
                newroom_id = str(message['newroom_id'])
                async_to_sync(self.channel_layer.group_add)(newroom_id, self.channel_name)
                print('Connected to room', newroom_id)

            if message['usersendcommandroom'] == 'message':
                room_id = str(message['room_id'])
                user_id = message['userid']
                username = UserMod.objects.get(id=user_id).name
                message = message['message']
                message_save = Message(author=UserMod.objects.get(id=user_id), room=Room.objects.get(id=room_id), text=message)
                message_save.save()
                print('Сообщение', message, 'сохранено в базе')
                async_to_sync(self.channel_layer.group_send)(room_id, {"type": "incoming_message", "order": "accept_message", "name": username, "message": message})
                print('Сообщение', message, 'отправлено в комнату', room_id)



