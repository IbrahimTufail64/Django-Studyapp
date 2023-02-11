from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm


# rooms = [
#     {'id': 1, 'name': 'ibrahim', 'room': 1},
#     {'id': 2, 'name': 'abdullah', 'room': 2},
# ]


def LoginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password does not exist')

    context = {page: 'login'}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.all()
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)
        | Q(name__icontains=q)
        | Q(description__icontains=q))
    room_messages = Message.objects.filter(
        Q(room__name__icontains=q) |
        Q(room__topic__name__icontains=q)
        | Q(room__description__icontains=q)
    )
    return render(request, 'base/home.html',
                  {'rooms': rooms, "topics": topics, "rooms_count": rooms.count(), "room_messages": room_messages})


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = Message.objects.filter(room=room)
    participants = room.participants.all()
    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login_page')
def form(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
        # form = RoomForm(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        ) 
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
        return redirect('home')
    return render(request, 'base/form.html', {'form': form, 'topics': topics})


@login_required(login_url='login_page')
def update(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    # if request.user != room.host:
    #     return HttpResponse('You are not the admin of this room!')

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, room: 'room'}
    return render(request, 'base/form.html', context)


@login_required(login_url='login_page')
def deleteForm(request, pk):
    room = Room.objects.get(id=pk)
    context = {'obj': room.name}
    if request.user != room.host:
        return HttpResponse('You are not the admin of this room!')
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete-form.html', context)


@login_required(login_url='login_page')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You can not delete this comment!')
    if request.method == "POST":
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request, 'base/delete-form.html', context)


def registerPage(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
            else:
                user = form.save(commit=False)
                user.username = username
                user.save()
                return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login_page')
def updateUser(request, pk):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/edit-user.html', {'form': form})
