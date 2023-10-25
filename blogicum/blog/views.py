import datetime
from typing import Any
# from django.db import models
from django.db.models.query import QuerySet

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect


from .models import Category, Post, User, Comment
from .forms import PostForm, CommentForm, EditUserForm
from django.views.generic import (
    UpdateView,
    DetailView,
    ListView,
    # CreateView,
    DeleteView,
    )
from django.contrib.auth.decorators import login_required
from .constants import POSTS_IN_PAGE
from django.db.models import Count
from django.core.paginator import Paginator
from django.urls import reverse_lazy, reverse


class IndexView(ListView):
    """ Главная страница """
    template_name = 'blog/index.html'
    paginate_by = POSTS_IN_PAGE
    queryset = post_list = Post.active_objects.all()


def post_detail(request, pk) -> HttpResponse:
    """ Страница постов """
    post = get_object_or_404(
        Post,
        pk=pk,
        is_published=True,
        category__is_published=True,
        pub_date__lte=datetime.datetime.now(),
    )
    context: dict = {'post': post}
    return render(request, 'blog/detail.html', context)


class CategoryListView(ListView):
    """ Страница категорий """
    paginate_by = POSTS_IN_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        category = get_object_or_404(
            Category.objects.filter(
                is_published=True,
                slug=self.kwargs['category_slug'],
            )
        )
        return category.posts.filter(
            is_published=True,
            pub_date__lte=datetime.datetime.now(),
            )


@login_required
def create_post(request):
    """ Страница создания постов """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'blog/create.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('blog:index')


def profile(request, username):
    """ Страница пользователя """
    user = get_object_or_404(User.objects.filter(username=username))
    posts = Post.objects.filter(
        author_id=user.id,).order_by('-pub_date').annotate(
            comment_count=Count('comments'),
            )
    paginator = Paginator(posts, POSTS_IN_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'profile': user,
        }
    return render(request, 'blog/profile.html', context)


class PostUpdateView(UpdateView):
    """Вью класс для формы редактирования поста."""

    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        """Функция проверки формы."""
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        get_object_or_404(
            Post,
            pk=kwargs['post_id'],
            is_published=True,
            author=self.request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        """Получение объекта поста для страницы."""
        return Post.objects.get(pk=self.kwargs['post_id'])


class PostDetailView(DetailView):
    """ Страница поста """
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        post = self.object
        context['post'] = post
        return context


# class CommentCreateView(CreateView):
#     post_obj = None
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/comment.html'
#     pk_url_kwarg = 'post_id'

#     def dispatch(self, request, *args, **kwargs):
#         self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.post_obj = self.post_obj
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('blog:post_detail',
# wargs={'post_id': self.post_obj.pk})

# class CommentCreateView(CreateView):
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/detail.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.post = self.post_obj
#         form.instance.author = self.request.user
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('blog:post_detail', kwargs={'poost_id': self.post_obj.id})

# class CommentCreateView(CreateView):
#     model = Comment
#     form_class = CommentForm
#     post_obj = None

#     def dispatch(self, request, *args, **kwargs):
#         self.post_obj = get_object_or_404(
#             Post,
#             id=kwargs['post_id'],
#             pub_date__lte=datetime.datetime.now(),
#             is_published=True,
#             category__is_published=True,
#         )
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.post = self.post_obj
#         return super().form_valid(form)

#     def get_success_url(self):
#         # return reverse(
#         #     'blog:post_detail',
#         #     kwargs={'post_id': self.kwargs['post_id']},
#         # )
#         return reverse('blog:post_detail', kwargs={'post_id': self.post_obj.id})


# class CommentCreateView(CreateView):
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/detail.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.post_obj = get_object_or_404(Post, id=kwargs['post_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.post = self.post_obj
#         form.instance.author = self.request.user
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('blog:post_detail', kwargs={'post_id': self.post_obj.id})

def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.posts = post
        comment.save()
    return redirect('blog:post_detail', post_id)


# class CommentCreateView(CreateView):
#     post_obj = None
#     model = Comment
#     class_form = CommentForm
#     template_name = 'blog/detail.html'
#     fields = '__all__'
#     pk_url_kwarg = 'post_id'

#     def dispatch(self, request, *args, **kwargs):
#         self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.post = self.post_obj
#         form.instance.author = self.request.user
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('blog:post_detail', kwargs={'post_id': self.post_obj.pk})


# def edit_comment(request, post_id, comment_id):
#     post = get_object_or_404(Post, pk=post_id)
#     instance = get_object_or_404(Comment, pk=comment_id)
#     form = CommentForm(request.POST or None, instance=instance)
#     context = {'form': form}
#     if form.is_valid():
#         comment = form.save(commit=False)
#         comment.author = request.user
#         comment.posts = post
#         comment.save()
#         return redirect('blog:post_detail', post_id)
#     return render(request, 'blog/comment.html', context)

# class CommentUpdateView(UpdateView):

#     model = Comment
#     form_class = CommentForm
#     pk_url_kwarg = 'post_id'
#     template_name = 'blog/comment.html'
#     url_kwarg = 'comment_id'

#     def dispatch(self, request, *args, **kwargs):
#         get_object_or_404(
#             Comment,
#             pk=kwargs['comment_id'],
#             post=kwargs['post_id'],
#             post__is_published=True,
#             author=self.get_object().pk
#         )
#         return super().dispatch(request, *args, **kwargs)

#     def get_success_url(self):
#         return reverse_lazy(
#             'blog:post_detail',
#             kwargs={'post_id': self.object.post_id},
    # self.object.post_id}

    # def get_object(self):
    #     return User.objects.get(username=self.request.user.username)


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:post_detail')
    url_kwarg = 'comment_id'


# class CommentUpdateView(UpdateView):
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/comment.html'
#     url_kwarg = 'comment_id'
#     pk_url_kwarg = 'post_id'

#     def dispatch(self, request, *args, **kwargs):
#         get_object_or_404(
#             Comment,
#             pk=kwargs['comment_id'],
#             post=kwargs['post_id'],
#             post__is_published=True,
#             author=self.get_object().pk
#         )
#         return super().dispatch(request, *args, **kwargs)

#     def get_success_url(self):
#         return reverse(
#             'blog/post_detail.html',
#             kwargs={'post_id': self.object.post_id},
#             )

class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comemnt.html'
    success_url = reverse_lazy('blog:detail')

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
            post=kwargs['post_id'],
            post__is_published=True,
            author=self.get_object().pk
        )
        return super().dispatch(request, *args, **kwargs)


def edit_profile(request):
    template = 'blog/user.html'
    form = EditUserForm(request.POST or None, request.user)
    context = {
        'form': form,
    }
    if form.is_valid():
        user = form.save(commit=False)
        user['password'] = User.objects.values('password')
        user['last_login'] = User.objects.values('last_login')
        user['id_superuser'] = User.objects.values('id_superuser')
        user['is_staff'] = User.objects.values('is_staff')
        user['is_active'] = User.objects.values('is_active')
        user['data_joined'] = User.objects.values('data_joined')
        user.save()
        return redirect('blog:profile', slug=request.user)
    return render(request, template, context)


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:profile')
