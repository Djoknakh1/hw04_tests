from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse
from django.shortcuts import render
# Функция reverse_lazy позволяет получить URL по параметрам функции path()
# Берём, тоже пригодится
from django.urls import reverse_lazy
# Create your views here.
from django.views.generic import CreateView

# Импортируем класс формы, чтобы сослаться на неё во view-классе
from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


def password_reset_form(request):
    # send_mail(
    #     "Заголовок1",
    #     "Тест",
    #     "agkuban@mail.ru",
    #     ["Djoknakh@yandex.ru"],
    # )
    subject = request.POST.get("subject", "")
    message = request.POST.get("message", "")
    from_email = request.POST.get("from_email", "")
    try:
        send_mail(subject, message, from_email, ["admin@example.com"])
    except BadHeaderError:
        return HttpResponse("Invalid header found.")

    return render(request, "users/password_reset_form.html")
