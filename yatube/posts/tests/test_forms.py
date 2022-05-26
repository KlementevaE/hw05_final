import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create_post(self):
        """Проверяем, что при создании поста создаётся новая запись в БД."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Текст поста из формы проверка',
            'image': uploaded,
        }
        response = self.authorized_client_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.order_by('pk').last().text,
                         form_data['text'])
        self.assertEqual(Post.objects.order_by('pk').last().image,
                         f'posts/{form_data["image"]}')
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': 'auth'}))

    def test_form_edit_post(self):
        """Проверяем, что при редактировании поста изменяется запись в БД."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текстовый пост проверка изменение',
        }
        response = (self.authorized_client_author.
                    post(reverse('posts:post_edit',
                                 kwargs={'post_id': self.post.pk}),
                         data=form_data, follow=True))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.pk}))

    def test_form_comment(self):
        """Проверяем, что комментарий появляется на странице поста."""
        form_data = {
            'text': 'Хороший пост',
        }
        response = (self.authorized_client.
                    post(reverse('posts:add_comment',
                                 kwargs={'post_id': self.post.pk}),
                         data=form_data, follow=True))
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.pk}))
        self.assertEqual(self.post.comments.order_by('pk').last().text,
                         form_data['text'])
