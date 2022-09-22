from posts.forms import PostForm
from posts.models import Post,Group
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group= Group.objects.create(
            title='Иван Иванов',
            slug='Ivanov',
            description='Группа Иванова',
        )

        cls.post_author = User.objects.create_user(
            username="post_author",
            first_name='Тестов',
            last_name='Тест',
            email='test@yatube.ru',
        )

        cls.post = Post.objects.create(
            group = PostFormTests.group,
            text = "Рандомный текст",
            author = User.objects.get(username='post_author'),
            )

        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.get(username='post_author')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.id,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse("posts:profile", kwargs={"username": self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Редактированный текст",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": 36}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": 36}),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(id=36, text="Редактированный текст").exists()
        )