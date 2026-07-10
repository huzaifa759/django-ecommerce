from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import LoginForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("core:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome — your account is ready.")
        return response


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Signed in as {form.get_user().username}.")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST" and request.user.is_authenticated:
            messages.info(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


@login_required
def account(request):
    return render(request, "users/account.html")
