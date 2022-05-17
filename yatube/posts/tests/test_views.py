import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Group, Post, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=small_gif,
                content_type='image/gif'
            )
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
            'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_context(self):
        """Шаблон index, group_list, profile сформирован с правильным
        контекстом.
        """
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for address in pages_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                first_object = response.context.get('page_obj').object_list[0]
                post_author_0 = first_object.author.username
                post_text_0 = first_object.text
                post_image_0 = first_object.image
                self.assertEqual(post_author_0, 'auth')
                self.assertEqual(post_text_0, 'Тестовый пост')
                self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': self.post.pk})))
        first_object = response.context.get('post')
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_create')))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = (self.authorized_client_author.
                    get(reverse('posts:post_edit',
                                kwargs={'post_id': self.post.pk})))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    COUNT_POST_FIRST_PAGE = 10
    COUNT_POST_SECOND_PAGE_GROUP_LIST = 3
    COUNT_POST_SECOND_PAGE_INDEX_PROFILE = 4

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        list_posts = []
        for i in range(1, 14):
            list_posts.append(Post.objects.create(author=cls.user,
                                                  text=f'Тестовый пост{i}',
                                                  group=cls.group))

        cls.post = list_posts

        cls.group = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test2-slug',
            description='Второе тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для второй тестовой группы',
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Паджинатор на 1 странице index, group_list, profile работает
        правильно.
        """
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for address in pages_names:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(len(response.context.get('page_obj')),
                                 self.COUNT_POST_FIRST_PAGE)

    def test_second_index_profile_page_contains_ten_records(self):
        """Паджинатор на 2 странице index, profile работает
        правильно.
        """
        pages_names = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for address in pages_names:
            with self.subTest(address=address):
                response = self.client.get(address + '?page=2')
                self.assertEqual(len(response.context.get('page_obj')),
                                 self.COUNT_POST_SECOND_PAGE_INDEX_PROFILE)

    def test_second_group_list_page_contains_three_records(self):
        """Паджинатор на 2 странице group_list работает правильно."""
        response = self.client.get(reverse('posts:group_list',
                                   kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')),
                         self.COUNT_POST_SECOND_PAGE_GROUP_LIST)

    def test_post_with_group_in_correct_group_list(self):
        """При создании пост попадает на страницу выбранной группы."""
        response = (self.client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': 'test2-slug'})))
        first_object = response.context.get('page_obj').object_list[0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0,
                         'Тестовый пост для второй тестовой группы')

    def test_post_with_group_not_in_correct_group_list(self):
        """При создании пост не попадает на страницу другой группы."""
        response = (self.client.
                    get(reverse('posts:group_list',
                        kwargs={'slug': 'test-slug'})))
        first_object = response.context.get('page_obj').object_list[0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, 'auth')
        self.assertNotEqual(post_text_0,
                            'Тестовый пост для второй тестовой группы')

    def test_follow_unfollow(self):
        """Проверка, что авторизованный пользователь может подписываться на
        других пользователей и удалять их из подписок.
        """
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': 'auth'}))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertEqual(User.objects.
                         get(following__user=self.user).username, 'auth')
        self.assertTrue(User.objects.
                        get(username='auth').following.
                        filter(user=self.user).exists())
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           kwargs={'username': 'auth'}))
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(User.objects.
                         get(username='auth').following.
                         filter(user=self.user).exists())

    def test_follow_in_correct_post_list(self):
        """Проверка, что пост пользователя появляется в ленте тех, кто
        подписан на него и не появляется в ленте тех, кто не подписан.
        """
        response = (self.authorized_client.
                    get(reverse('posts:follow_index')))
        follow_index_emply = response.context.get('page_obj')
        self.assertEqual(len(follow_index_emply), 0)
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': 'auth'}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        follow_index_full = response.context.get('page_obj')
        self.assertEqual(len(follow_index_full), self.COUNT_POST_FIRST_PAGE)


class CacheTests(TestCase):
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
            text='Проверка кэширования',
            group=cls.group,
        )
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.user)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_cache_index_page(self):
        self.client.get(reverse('posts:index'))
        Post.objects.get(pk=self.post.pk).delete()
        response_before = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response_before.content.decode('utf-8').
                            find(self.post.text), -1)
        cache.clear()
        response_after = self.client.get(reverse('posts:index'))
        self.assertEqual(response_after.content.decode('utf-8').
                         find(self.post.text), -1)
