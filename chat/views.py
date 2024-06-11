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
    return render(request, 'base/lobby.html')


def room(request):
    return render(request, 'base/room.html')


def getToken(request):
    appId = settings.AGORA_APP_ID
    appCertificate = settings.AGORA_APP_CERTIFICATE
    channelName = request.GET.get('channelName')
    if channelName is None:
        return JsonResponse({'error': 'channel name is required'}, status=400)

    uid = random.randint(1, 230)
    expirationTimeInSeconds = 3600
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    return JsonResponse({'token': token, 'uid': uid}, safe=False)


@csrf_exempt
def createMember(request):
    try:
        data = json.loads(request.body)
        member, created = RoomMember.objects.get_or_create(
            name=data['name'],
            uid=data['UID'],
            room_name=data['room_name']
        )
        return JsonResponse({'name': data['name']}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')

    try:
        member = RoomMember.objects.get(uid=uid, room_name=room_name)
        return JsonResponse({'name': member.name}, safe=False)
    except RoomMember.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)


@csrf_exempt
def deleteMember(request):
    try:
        data = json.loads(request.body)
        if not data.get('name') or not data.get('room_name') or not data.get('UID'):
            return JsonResponse({'error': 'Incomplete data for deletion'}, status=400)

        member = RoomMember.objects.get(name=data['name'], uid=data['UID'], room_name=data['room_name'])
        member.delete()
        return JsonResponse('Member deleted', safe=False)
    except RoomMember.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

