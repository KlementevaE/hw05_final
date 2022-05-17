from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_guest_client(self):
        """Страницы доступны любому пользователю."""
        url_list = [
            '/',
            '/group/test-slug/',
            '/profile/auth/',
            f'/posts/{self.post.pk}/',
            f'/posts/{self.post.pk}/edit/',
        ]
        for address in url_list:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_comment(self):
        """Страница по адресу /posts/{self.post.pk}/comment/ перенаправит
        авторизованного пользователя на страницу поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/comment/', follow=True)
        self.assertRedirects(
            response, f'/posts/{self.post.pk}/'
        )

    def test_post_comment_url_redirect_anonymous_on_login(self):
        """Страница перенаправит анонимного пользователя на страницу логина."""
        url_redirect_url = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.pk}/comment/':
            f'/auth/login/?next=/posts/{self.post.pk}/comment/',
        }
        for address, address_redirect in url_redirect_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertRedirects(response, address_redirect)

    def test_unexicting_page(self):
        """Проверка запроса к несуществующей странице."""
        response = self.guest_client.get('/unexicting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_guest_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон (любой пользователь)."""
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/post_detail.html',
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон (зарегистрированный)."""
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/post_detail.html',
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_author_post_correct_template(self):
        """URL-адрес использует соответствующий шаблон (автор поста)."""
        url_names_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for address, template in url_names_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)
