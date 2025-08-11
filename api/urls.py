from django.urls import path
from .views import RegisterView, LoginView, LogoutView, GenerateContentView,save_user_keys

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('generate/', GenerateContentView.as_view(), name='generate_content'),
    path('set-keys/', save_user_keys, name='save_user_keys'),
]
