from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from collections import ChainMap

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)


class TestURLs(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post_author = User.objects.create(username="test_author")
        cls.other_user = User.objects.create(username="test_other_user")
        group = Group.objects.create(
            title="Test group",
            slug="test_group",
            description="Test group",
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text="test post",
        )
        # urls accessible to anyone
        cls.public_urls = {
            "/": "posts/index.html",
            f"/group/{group.slug}/": "posts/group_list.html",
            f"/profile/{cls.post_author.username}/": "posts/profile.html",
            f"/posts/{cls.post.id}/": "posts/post_detail.html",
        }
        # urls which require client to be authorized
        cls.login_required_urls = {
            "/create/": "posts/create_post.html",
        }
        # urls only accessible to post author
        cls.author_only_urls = {
            f"/posts/{cls.post.id}/edit/": "posts/create_post.html",
        }

    def setUp(self):
        self.anonymous_client = Client()
        self.post_author_client = Client()
        self.other_user_client = Client()
        self.post_author_client.force_login(TestURLs.post_author)
        self.other_user_client.force_login(TestURLs.other_user)

    def test_public(self):
        for url in TestURLs.public_urls:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_existent_page_returns_404(self):
        response = self.anonymous_client.get("/non_existent_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_anonymous_user_is_redirected_to_login_page(self):
        login_required_urls = [
            *TestURLs.login_required_urls,
            *TestURLs.author_only_urls,
        ]
        for url in login_required_urls:
            with self.subTest(url=url):
                response = self.anonymous_client.get(url)
                expected_redirect_url = f"/auth/login/?next={url}"
                self.assertRedirects(response, expected_redirect_url)

    def test_authorized_user_can_view_login_required_urls(self):
        for url in TestURLs.login_required_urls:
            with self.subTest(url=url):
                response = self.other_user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_can_view_author_only_pages(self):
        for url in TestURLs.author_only_urls:
            with self.subTest(url=url):
                response = self.post_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_non_author_user_cannot_edit_post(self):
        post_id = TestURLs.post.id
        response = self.other_user_client.get(f"/posts/{post_id}/edit/")
        self.assertRedirects(response, f"/posts/{post_id}/")

    def test_correct_template(self):
        url_templates = ChainMap(
            TestURLs.public_urls,
            TestURLs.login_required_urls,
            TestURLs.author_only_urls,
        )
        for url, template in url_templates.items():
            with self.subTest(path=url):
                response = self.post_author_client.get(url)
                self.assertTemplateUsed(response, template)


# class PostURLTests(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         # Создадим запись в БД для проверки доступности адреса task/test-slug/
#         Post.objects.create(
#             title="Тестовый заголовок", text="Тестовый текст", slug="test-slug"
#         )

#     def setUp(self):
#         # Создаем неавторизованный клиент
#         self.guest_client = Client()
#         # Создаем пользователя
#         self.user = User.objects.create_user(username="HasNoName")
#         # Создаем второй клиент
#         self.authorized_client = Client()
#         # Авторизуем пользователя
#         self.authorized_client.force_login(self.user)

#     # Проверка вызываемых шаблонов для каждого адреса
#     def test_home_url_uses_correct_template(self):
#         response = self.guest_client.get("/")
#         self.assertTemplateUsed(response, "posts/index.html")

#     def test_group_url_uses_correct_template(self):
#         response = self.guest_client.get("group/<slug:slug>/")
#         self.assertTemplateUsed(response, "posts/group_list.html")

#     def test_post_profile_list_url_uses_correct_template(self):
#         response = self.guest_client.get("profile/<str:username>/")
#         self.assertTemplateUsed(response, "posts/profile.html")

#     def test_post_detail_url_uses_correct_template(self):
#         response = self.authorized_client.get("posts/<int:post_id>/")
#         self.assertTemplateUsed(response, "posts/post_detail.html")

#     def test_create_url_uses_correct_template(self):
#         response = self.authorized_client.get("create/")
#         self.assertTemplateUsed(response, "posts/create_post.html")
