from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/create/', views.create_post, name='craete_post'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryListView.as_view(),
        name='category_posts',
        ),
    # path(
    #     'posts/<int:post_id>/edit/',
    #     views.EditPostUpdateView.as_view(),
    #     name='edit_post',
    # ),
    path('profile/<str:username>/', views.profile, name='profile'),
    # path(
    #     'posts/<int:post_id>/comment/',
    #     views.CommentCreateView.as_view(),
    #     name='add_comment',
    # ),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment',
    ),
    path(
        'posts/<int:pk>/',
        views.PostDetailView.as_view(),
        name='post_detail',
        ),
    path('edit_profile/',
         views.edit_profile,
         name='edit_profile',
         ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post',
        ),
    path(
        'posts/<int:pk>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post',
        ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment',
        ),
    # path(
    #     'posts/<int:post_id>/edit_comment/<int:comment_id>/',
    #     views.edit_comment,
    #     name='edit_comment',
    # ),
    # path(
    #     'posts/<slug:post_id>/delete_comment/<slug:comment_id>/',
    #     views.CommentDeleteView.as_view(),
    #     name='delete_comment',
    # ),
]
