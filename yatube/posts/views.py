from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Post, Group, User

PER_PAGE = 10


def paginate(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    page_obj = paginate(request)
    # Отдаем в словаре контекста
    context = {
        "page_obj": page_obj,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    page_obj = paginate(request)

    posts = group.posts.all()[:PER_PAGE]
    context = {
        "group": group,
        "posts": posts,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author__username=username)
    paginator = Paginator(posts, PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    count = posts.count()
    context = {
        "count": count,
        "page_obj": page_obj,
        "author": author,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    # Здесь код запроса к модели и создание словаря контекста
    post_alone = get_object_or_404(Post, pk=post_id)
    posts = Post.objects.filter(pk=post_id)
    count = Post.objects.filter(author=post_alone.author).count()
    context = {
        "post_alone": post_alone,
        "count": count,
        "posts": posts,
    }
    return render(request, "posts/post_detail.html", context=context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:profile", username=post.author)

    context = {"form": form}
    return render(request, "posts/create_post.html", context)


@login_required
def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, id=post_id)
    if request.user != edit_post.author:
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(request.POST or None, instance=edit_post)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id=post_id)
    template = "posts/create_post.html"
    context = {"form": form, "is_edit": True}
    return render(request, template, context)
