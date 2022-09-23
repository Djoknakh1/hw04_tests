from http import HTTPStatus

from django.urls import reverse
from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Группа для теста",
        )
        Post.objects.create(
            id=1,
            text="Тестовый пост",
            author=User.objects.create_user(username="HasNoName"),
        )
        cls.templates_url_names = {
            "/": "posts/index.html",
            "/group/test-slug/": "posts/group_list.html",
            "/profile/HasNoName/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
        }
        cls.url_templates_names = {
            "/create/": "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
        }
        cls.wrong_urls = {
            "general": "/wrong-url/",
            "group_list": "/group/wrong-test-slug/",
            "profile": "/profile/HasName/",
            "post_detail": "/posts/10/",
            "post_edit": "/posts/a/edit/",
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username="HasNoName")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user = User.objects.create(username="NoName")
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user)

    def test_urls_exists_and_uses_correct_template_unauthorized(self):
        """Проверяем,что urls работают правильно и используют правильный шаблон
        для не авторизированного пользователя"""
        for address, template in PostURLTests.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_exists_and_uses_correct_template_authorized(self):
        """Проверяем,что urls работают правильно и используют правильный шаблон
        для авторизированного пользователя"""
        for address, template in PostURLTests.url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_url_unauthorized_redirects(self):
        """Проверяем перенаправление не авторизированных пользователей"""
        url_templates_names = {
            "/create/": "/auth/login/?next=/create/",
            "/posts/1/edit/": "/auth/login/?next=/posts/1/edit/",
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, template)

    def test_non_author_user_redirect(self):
        """Проверяем что только автор поста может его редактировать"""
        response = self.authorized_client_2.get(
            reverse("posts:post_edit", kwargs={"post_id": 1})
        )
        self.assertRedirects(
            response, reverse("posts:post_detail", kwargs={"post_id": 1})
        )

    def test_non_existent_url_returns_404(self):
        """Проверяем что ссылки на несуществующие объекты выдают ошибку 404"""
        for name, address in PostURLTests.wrong_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
