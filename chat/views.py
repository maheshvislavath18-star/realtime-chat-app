from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User

from .models import Room, Message


# ---------------- HOME ----------------
def chat_home(request):

    rooms = Room.objects.all()
    recent_chats = []

    for room in rooms:

        last_msg = Message.objects.filter(room=room).order_by('-created_at').first()

        recent_chats.append({
            "room": room,
            "last_message": last_msg.content if last_msg else "",
            "time": last_msg.created_at if last_msg else None
        })

    return render(request, 'chat/home.html', {
        'recent_chats': recent_chats
    })


# ---------------- PRIVATE CHAT ----------------
def private_chat(request, user2):

    user1 = request.user.username
    room_name = "_".join(sorted([user1, user2]))

    room, created = Room.objects.get_or_create(name=room_name)

    messages = Message.objects.filter(room=room).order_by('created_at')

    # ---------------- SEND MESSAGE ----------------
    if request.method == 'POST':

        message = request.POST.get('message', '')
        image = request.FILES.get('image')

        msg = Message.objects.create(
            room=room,
            user=request.user,
            content=message,
            image=image
        )

        # AJAX response (for fetch API)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            return JsonResponse({
                "id": msg.id,
                "message": msg.content,
                "image_url": msg.image.url if msg.image else None,
                "username": request.user.username
            })

        return redirect('private_chat', user2=user2)

    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages,
        'user2': user2
    })


# ---------------- GROUP CHAT ----------------
def room_view(request, room_name):

    room = get_object_or_404(Room, name=room_name)

    messages = Message.objects.filter(room=room).order_by('created_at')

    # ---------------- SEND MESSAGE ----------------
    if request.method == 'POST':

        message = request.POST.get('message', '')
        image = request.FILES.get('image')

        msg = Message.objects.create(
            room=room,
            user=request.user,
            content=message,
            image=image
        )

        # AJAX response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':

            return JsonResponse({
                "id": msg.id,
                "message": msg.content,
                "image_url": msg.image.url if msg.image else None,
                "username": request.user.username
            })

        return redirect('room', room_name=room.name)

    return render(request, 'chat/room.html', {
        'room': room,
        'messages': messages
    })