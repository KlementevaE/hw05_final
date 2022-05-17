from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import NUM_SYMBOLS, Group, Post, Comment

User = get_user_model()


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост очень очень длинный',
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=User.objects.create_user(username='HasNoName'),
            text='Интересная история!'
        )

    def test_models_group_have_correct_title(self):
        """Проверяем, что у моделей Group корректно работает __str__."""
        group = self.group
        expected_object_title = group.title
        self.assertEqual(f'<Group {expected_object_title}>', str(group))

    def test_models_post_have_correct_content_text(self):
        """Проверяем, что у моделей Post корректно работает __str__."""
        max_length_text = NUM_SYMBOLS
        post = self.post
        expected_object_text = post.text[:max_length_text]
        self.assertEqual(expected_object_text, str(post))

    def test_models_coment_have_correct_content_text(self):
        """Проверяем, что у моделей Cmment корректно работает __str__."""
        max_length_text = NUM_SYMBOLS
        comment = self.comment
        expected_object_text = comment.text[:max_length_text]
        self.assertEqual(expected_object_text, str(comment))
