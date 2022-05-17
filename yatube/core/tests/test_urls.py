from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache


User = get_user_model()


class CoreURLTests(TestCase):
    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_guest_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон (любой пользователь)."""
        response = self.guest_client.get('core.views.page_not_found')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_authorized_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон (зарегистрированный)."""
        response = self.authorized_client.get('core.views.page_not_found')
        self.assertTemplateUsed(response, 'core/404.html')
