from django.urls import path
from .views import (
    CreatepostView, 
    ListPostView, 
    ViewAPostView, 
    UpdatePostView, 
    DeletePostView, 
    CreateCommentView, 
    ListCommentView,
    UpdateCommentView,
    DeleteCommentView,
)


urlpatterns = [
    path('create/', CreatepostView.as_view(), name='create_post'),
    path('list/', ListPostView.as_view(), name='list_posts'),
    path('view/<int:pk>/', ViewAPostView.as_view(), name='view_post'),
    path('update/<int:pk>/', UpdatePostView.as_view(), name='update_post'),
    path('delete/<int:pk>/', DeletePostView.as_view(), name='delete_post'),
    path('create/<int:pk>/comments/', CreateCommentView.as_view(), name='create_comment'),
    path('list/<int:pk>/comments/', ListCommentView.as_view(), name='list_comments'),
    path('update/<int:pk>/comments/', UpdateCommentView.as_view(), name='update_comment'),
    path('delete/comments/<int:pk>/', DeleteCommentView.as_view(), name='delete_comment'),
]