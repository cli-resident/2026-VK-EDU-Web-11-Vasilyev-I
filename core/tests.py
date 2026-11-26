import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from .forms import SignupForm
from .models import Profile


class AccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('ivan', password='Good-password-913', email='ivan@example.com')
        Profile.objects.create(user=self.user)

    def test_login_next(self):
        response = self.client.post('/login/?next=/hot/', {'username': 'ivan', 'password': 'Good-password-913', 'next': '/hot/'})
        self.assertRedirects(response, '/hot/')
        self.client.logout()
        response = self.client.post('/login/', {'username': 'ivan', 'password': 'Good-password-913', 'next': 'https://example.org/'})
        self.assertRedirects(response, '/')

    def test_invalid_login_and_csrf(self):
        response = self.client.post('/login/', {'username': 'ivan', 'password': 'wrong'})
        self.assertContains(response, 'ivan')
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Client(enforce_csrf_checks=True).post('/login/', {}).status_code, 403)

    def test_signup_and_password_validation(self):
        data = {'username': 'anna', 'email': 'anna@example.com', 'first_name': 'Анна', 'password1': '123', 'password2': '123'}
        self.assertFalse(SignupForm(data).is_valid())
        data.update(password1='Different-pass-721', password2='Different-pass-721')
        self.assertRedirects(self.client.post('/signup/', data), '/')
        self.assertTrue(Profile.objects.filter(user__username='anna').exists())

    def test_profile_upload_and_logout(self):
        self.assertEqual(self.client.get('/profile/').status_code, 302)
        self.client.force_login(self.user)
        content = BytesIO()
        Image.new('RGB', (8, 8)).save(content, format='PNG')
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            avatar = SimpleUploadedFile('avatar.png', content.getvalue(), content_type='image/png')
            response = self.client.post('/profile/', {'email': 'new@example.com', 'first_name': 'Иван', 'avatar': avatar})
            self.assertRedirects(response, '/profile/')
            self.user.profile.refresh_from_db()
            self.assertTrue(self.user.profile.avatar.name.startswith('avatars/'))
            self.assertNotIn('avatar.png', self.user.profile.avatar.name)
            bad = SimpleUploadedFile('file.png', b'not an image', content_type='image/png')
            response = self.client.post('/profile/', {'email': 'new@example.com', 'first_name': 'Иван', 'avatar': bad})
            self.assertTrue(response.context['form'].errors)
        self.assertEqual(self.client.get('/logout/').status_code, 405)
        self.assertRedirects(self.client.post('/logout/', {'next': '/hot/'}), '/hot/')


class AdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser('admin', 'admin@example.com', 'Admin-test-918')
        Profile.objects.create(user=self.user)
        self.client.force_login(self.user)

    def test_admin_models_and_inline(self):
        for model in ['question', 'answer', 'tag', 'questionlike', 'answerlike']:
            with self.subTest(model=model):
                self.assertEqual(self.client.get(f'/admin/questions/{model}/').status_code, 200)
                self.assertEqual(self.client.get(f'/admin/questions/{model}/add/').status_code, 200)
        self.assertEqual(self.client.get('/admin/core/profile/').status_code, 200)
        response = self.client.get(f'/admin/auth/user/{self.user.pk}/change/')
        self.assertContains(response, 'profile-0-avatar')

    def test_avatar_limits(self):
        from django.core.exceptions import ValidationError
        from .forms import validate_avatar
        for name, content in [('large.png', b'x' * (5 * 1024 * 1024 + 1)), ('avatar.svg', b'<svg/>')]:
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_avatar(SimpleUploadedFile(name, content))
