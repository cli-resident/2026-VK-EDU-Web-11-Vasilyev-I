from pathlib import Path

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Profile


class StyledForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['aria-describedby'] = f'id_{name}_errors'
            if self.is_bound and name in self.errors:
                field.widget.attrs['class'] += ' is-invalid'
                field.widget.attrs['aria-invalid'] = 'true'


def validate_avatar(avatar):
    if avatar and hasattr(avatar, 'size'):
        if avatar.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер изображения не должен превышать 5 МБ.')
        if Path(avatar.name).suffix.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
            raise forms.ValidationError('Выберите изображение JPG, PNG или WebP.')
    return avatar


class LoginForm(StyledForm, AuthenticationForm):
    pass


class SignupForm(StyledForm, UserCreationForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='Имя', max_length=150)
    avatar = forms.ImageField(label='Аватар', required=False, validators=[validate_avatar])

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password1', 'password2', 'avatar']

    def clean_email(self) -> str:
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        Profile.objects.create(user=user, avatar=self.cleaned_data.get('avatar'))
        return user


class ProfileForm(StyledForm, forms.ModelForm):
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='Имя', max_length=150)
    avatar = forms.ImageField(label='Аватар', required=False, validators=[validate_avatar])

    class Meta:
        model = User
        fields = ['email', 'first_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].initial = self.instance.profile.avatar

    def clean_email(self) -> str:
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот email уже используется.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save()
        profile = user.profile
        avatar = self.cleaned_data.get('avatar')
        if avatar is False:
            profile.avatar = ''
        elif avatar:
            profile.avatar = avatar
        profile.save()
        return user
