from posts.forms import PostForm
from posts.models import Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            id=42,
            text="Текст",
            author=User.objects.create(username="Bazz"),
        )
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.get(username="Bazz")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст",
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
            reverse("posts:post_edit", kwargs={"post_id": 42}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": 42}),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(id=42, text="Редактированный текст").exists()
        )
