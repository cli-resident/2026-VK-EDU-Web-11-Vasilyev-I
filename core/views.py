from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileForm, SignupForm


class Login(LoginView):
    template_name = 'core/login.html'
    authentication_form = LoginForm
    next_page = 'questions:index'
    redirect_authenticated_user = True


def signup(request):
    form = SignupForm(request.POST if request.method == 'POST' else None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        auth_login(request, form.save())
        return redirect('questions:index')
    return render(request, 'core/signup.html', {'form': form})


@login_required
def profile(request):
    form = ProfileForm(request.POST if request.method == 'POST' else None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('core:profile')
    return render(request, 'core/profile.html', {'form': form})


@require_POST
def logout(request):
    destination = request.POST.get('next', '/')
    if not url_has_allowed_host_and_scheme(destination, {request.get_host()}, require_https=request.is_secure()):
        destination = reverse('questions:index')
    auth_logout(request)
    return redirect(destination)
