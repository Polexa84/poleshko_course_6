from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from django.contrib.auth.views import PasswordResetView

app_name = 'users'


class MyPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


urlpatterns = [
    # Основные URL аутентификации
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('confirm_email/<str:uidb64>/<str:token>/',
         views.confirm_email,
         name='confirm_email'),

    # URL сброса пароля
    path('password_reset/',
         MyPasswordResetView.as_view(),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="users/password_reset_done.html"
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="users/password_reset_confirm.html",
             form_class=CustomSetPasswordForm,
             success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="users/password_reset_complete.html"
         ),
         name='password_reset_complete'),
]