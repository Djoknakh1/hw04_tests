from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="Bazz")
        Post.objects.create(
            text="Текст",
            author=PostCreateFormTests.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_id = Post.objects.get(text="Текст").id

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
            reverse(
                "posts:profile",
                kwargs={"username": PostCreateFormTests.user.username},
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
            ).exists()
        )
        self.assertEqual(
            Post.objects.get(
                text=form_data["text"],
            ),
            Post.objects.latest("pub_date"),
        )

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        form_data = {
            "text": "Редактированный текст",
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"post_id": self.post_id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": self.post_id}),
        )

        self.assertTrue(
            Post.objects.filter(
                id=self.post_id, text="Редактированный текст"
            ).exists()
        )
