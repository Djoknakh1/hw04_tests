from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        '''Создание тестовых записей в БД'''
        super().setUpClass()

        cls.post_author = User.objects.create_user(username="test_author")
        cls.group = Group.objects.create(
            title = "Иван Иванович",
            slug = "ivan_ivanovich",
            description = "Группа Ивана Ивановича",
        )

        cls.post = Post.objects.create(
            text = "Рандомный текст",
            group = cls.group,
            author = cls.post_author,
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'author': 'Автор поста',
            'text': 'Текст поста',
            'group': 'Тег группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Слаг',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

        def test_help_text(self):
            """help_text в полях совпадает с ожидаемым."""
            post = PostModelTest.post
            field_help_texts = {
                'text': 'Введите текст поста',
                'group': 'Группа, к которой относится пост',
            }
            for value, expected in field_help_texts.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        post._meta.get_field(value).help_text, expected)

            group = PostModelTest.group
            field_help_texts = {
                'slug': 'Слаг группы',
            }
            for value, expected in field_help_texts.items():
                with self.subTest(value=value):
                    self.assertEqual(
                        post._meta.get_field(value).help_text, expected)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        group_str = group.title
        self.assertEqual(group_str, str(group))

    def test_object_name_is_text_field(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        post_str = post.text
        self.assertEqual(post_str, str(post))