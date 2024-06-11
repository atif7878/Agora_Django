from django.shortcuts import render
from django.http import JsonResponse
import random
import time
from agora_token_builder import RtcTokenBuilder
from chat_with_agora_into_django import settings
from .models import RoomMember
import json
from django.views.decorators.csrf import csrf_exempt

def lobby(request):
    print("Lobby page accessed")
    return render(request, 'base/lobby.html')

def room(request):
    print("Room page accessed")
    return render(request, 'base/room.html')

def getToken(request):
    print("getToken called")
    appId = settings.AGORA_APP_ID
    appCertificate = settings.AGORA_APP_CERTIFICATE
    channelName = request.GET.get('channelName')
    if channelName is None:
        print("Channel name is missing")
        return JsonResponse({'error': 'channel name is required'}, status=400)

    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    print(f"Token generated: {token}, UID: {uid}")
    return JsonResponse({'token': token, 'uid': uid}, safe=False)

@csrf_exempt
def createMember(request):
    print("createMember called")
    try:
        data = json.loads(request.body)
        print("Data received:", data)
        member, created = RoomMember.objects.get_or_create(
            name=data['name'],
            uid=data['UID'],
            room_name=data['room_name']
        )
        print(f"Member created: {member}")
        return JsonResponse({'name': data['name']}, safe=False)
    except Exception as e:
        print("Error in createMember:", e)
        return JsonResponse({'error': str(e)}, status=500)

def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')
    print(f"getMember called with UID: {uid}, room_name: {room_name}")

    try:
        member = RoomMember.objects.get(uid=uid, room_name=room_name)
        print(f"Member found: {member}")
        return JsonResponse({'name': member.name}, safe=False)
    except RoomMember.DoesNotExist:
        print("Member not found")
        return JsonResponse({'error': 'Member not found'}, status=404)


@csrf_exempt
def deleteMember(request):
    print("deleteMember called")
    try:
        data = json.loads(request.body)
        print("Data received for deletion:", data)
        if not data.get('name') or not data.get('room_name') or not data.get('UID'):
            return JsonResponse({'error': 'Incomplete data for deletion'}, status=400)

        member = RoomMember.objects.get(name=data['name'], uid=data['UID'], room_name=data['room_name'])
        member.delete()
        print(f"Member deleted: {member}")
        return JsonResponse('Member deleted', safe=False)
    except RoomMember.DoesNotExist:
        print("Member not found for deletion")
        return JsonResponse({'error': 'Member not found'}, status=404)
    except Exception as e:
        print("Error in deleteMember:", e)
        return JsonResponse({'error': str(e)}, status=500)

