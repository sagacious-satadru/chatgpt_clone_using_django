from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from django.contrib import auth

from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

# Create your views here.


from decouple import config

openai_api_key = config('OPENAI_API_KEY')
openai.api_key = openai_api_key

def ask_openai(message):
    response = openai.ChatCompletion.create(
        # model = "text-davinci-003",
        model = "gpt-3.5-turbo",
        # prompt = message,
        # max_tokens = 150,
        # n = 1,
        # stop = None,
        # temperature = 0.7,
        messages = [
            {'role' : "system", "content" : "You are a playful assistant."},
            {"role" :  "user", "content" : message},
        ]
    )
    # print(response)

    # answer = response.choices[0].text.strip()
    answer = response.choices[0].message.content.strip()
    return answer


def chatbot(request):
    chats = Chat.objects.filter(user = request.user) # filters the messages(i.e. the chats) of the currently logged in user from the host of chats that might be currently stored in the database

    if request.method == 'POST':
        message = request.POST.get('message')
        # response = 'Hello Satadru!'
        response = ask_openai(message)
        # before returning the response to the user, we'd like to save the current chat in our database so that when the user logs back in again, they're able to continue from where they left
        chat = Chat(user = request.user, message = message, response = response, created_at = timezone.now()) # request.user gives us the user who's currntly logged in, and as for the other attributes of the Chat class (which represnts the Chat table), i.e. 'message' is set equal to the message sent to the chatbot by the user, and 'response' = the response received from the API (the chatbot). The created_at is set equal to the local time of the chat in the user's timezone
        chat.save()
        return JsonResponse({'message' : message, 'response' : response})
    return render(request, 'chatbot.html', {'chats' : chats}) # we render the chats of the currently logged in user, loaded from the database, on the page as well 

def login(request):
    # if request.method == 'POST':
    #     username = request.POST['username']
    #     password = request.POST['password']
    #     user = auth.authenticate(request, username=username, password=password)
    #     if user is not None:
    #         auth.login(request, user)
    #         return redirect('chatbot')
    #     else:
    #         error_message = 'Invalid username or password'
    #         return render(request, 'login.html', {'error_message': error_message})
    # else:
    # username = 'Satadru', password = 'boba'
    if request.method == 'POST':
        username = request.POST['username'] # if we look at the 'login' HTML page, we'll see an i/p form which takes in the username and has a name = 'username', and another password i/p field, which has a name = 'password'
        password = request.POST['password']
        user = auth.authenticate(request, username = username, password = password)
        if user is not None: # if the user is not invalid, i.e. the user exists in the database
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = "Invalid username or passoword"
            return render(request, 'login.html', {'error_message' : error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Make sure the 2 passwords match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')