from django.urls import path
from .views import CustomUserLoginView, CustomUserRegisterView, CustomUserProfileView, UpdateCustomUserProfileView, ChangePasswordView, DeleteAccountView

urlpatterns = [
    path('login/', CustomUserLoginView.as_view(), name='login'),
    path('register/', CustomUserRegisterView.as_view(), name='register'),
    path('profile/', CustomUserProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateCustomUserProfileView.as_view(), name='update_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    
]
