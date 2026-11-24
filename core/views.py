from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def login(request: HttpRequest) -> HttpResponse:
    return render(request, 'core/login.html')


def signup(request: HttpRequest) -> HttpResponse:
    return render(request, 'core/signup.html')


def profile(request: HttpRequest) -> HttpResponse:
    return render(request, 'core/profile.html', {'profile_page': True})
