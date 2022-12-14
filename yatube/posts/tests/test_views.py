from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create(username="Bazz")
        Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
        )
        post_objs = [
            Post(
                text=f"Пост №{i+1}",
                author=User.objects.get(username="Bazz"),
                group=Group.objects.get(slug="test-slug"),
            )
            for i in range(15)
        ]
        Post.objects.bulk_create(post_objs)
        cls.last_post_id = Post.objects.latest("pub_date").id
        cls.templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "posts/group_list.html",
            reverse("posts:post_create"): "posts/create_post.html",
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostPagesTests.last_post_id},
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit",
                kwargs={"post_id": PostPagesTests.last_post_id},
            ): "posts/create_post.html",
            reverse(
                "posts:profile",
                kwargs={"username": "Bazz"},
            ): "posts/profile.html",
        }

    def setUp(self):
        self.user = User.objects.get(username="Bazz")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.get(slug="test-slug")

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for (
            reverse_name,
            template,
        ) in PostPagesTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_and_sorting_by_pubdate(self):
        """Проверяем что paginator работает
        на страницах профиля, групп, главной и они отсортированы по дате
        создания"""
        FIELDS = [
            PostPagesTests.last_post_id,
            f"Пост №{PostPagesTests.last_post_id}",
            self.user,
            self.group,
        ]
        view_funcs = {
            reverse("posts:index"): "?page=2",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug"}
            ): "?page=2",
            reverse("posts:profile", kwargs={"username": "Bazz"}): "?page=2",
        }
        for reverse_name, page_number in view_funcs.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context["page_obj"]), 10)
                response = self.client.get(reverse_name + page_number)
                self.assertEqual(len(response.context["page_obj"]), 5)
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.id, FIELDS[0])
                self.assertEqual(first_object.text, FIELDS[1])
                self.assertEqual(first_object.author, FIELDS[2])
                self.assertEqual(first_object.group, FIELDS[3])

    def test_forms_pages(self):
        """Проверяем страницы с формами"""
        view_funcs = {
            reverse("posts:post_create"): forms.ModelForm,
            reverse(
                "posts:post_edit", kwargs={"post_id": 10}
            ): forms.ModelForm,
        }
        for reverse_name, clss in view_funcs.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                form_obj = response.context["form"]
                self.assertIsInstance(form_obj, clss)

    def test_post_detail(self):
        """Проверяем словарь подробной информации о записи"""
        response = self.client.get(
            reverse(
                "posts:post_detail",
                kwargs={"post_id": PostPagesTests.last_post_id},
            )
        )
        obj = response.context["post_alone"]
        fields = {
            obj.id: PostPagesTests.last_post_id,
            obj.text: f"Пост №{PostPagesTests.last_post_id}",
            obj.author: self.user,
            obj.group: self.group,
        }
        for field, correct_field in fields.items():
            self.assertEqual(field, correct_field)

    def test_form_post_creation(self):
        FIELDS = [
            "Test post creation",
            self.user,
            self.group,
        ]
        Post.objects.create(text=FIELDS[0], author=FIELDS[1], group=FIELDS[2])
        view_funcs = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": "test-slug"}),
            reverse("posts:profile", kwargs={"username": "Bazz"}),
        ]
        for reverse_name in view_funcs:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                first_object = response.context["page_obj"][0]
                self.assertEqual(first_object.text, FIELDS[0])
                self.assertEqual(first_object.author, FIELDS[1])
                self.assertEqual(first_object.group, FIELDS[2])
