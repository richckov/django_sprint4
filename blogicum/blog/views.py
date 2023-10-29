import datetime

from core.mixins import AuthorshipMixin, ScuccesUrlPostDetail
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import POSTS_IN_PAGE
from .forms import CommentForm, EditUserForm, PostForm
from .models import Category, Comment, Post, User


def get_some_queryset():
    return Post.objects.select_related(
            'author',
            'location',
            'category'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.datetime.now()
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class IndexListView(ListView):
    """ Главная страница """
    template_name = 'blog/index.html'
    paginate_by = POSTS_IN_PAGE
    queryset = Post.active_objects.all()
    ordering = '-pub_date'


class CategoryListView(ListView):
    """ Страница категорий """
    paginate_by = POSTS_IN_PAGE
    template_name = 'blog/category.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        slug = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        context['category'] = slug
        return context

    def get_queryset(self):
        category = get_object_or_404(
            Category.objects.filter(
                is_published=True,
                slug=self.kwargs['category_slug'],
            )
        )
        return category.posts.filter(
            is_published=True,
            pub_date__lte=datetime.datetime.now(),
            ).order_by('-pub_date').annotate(comment_count=Count('comments'))


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author},
        )


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


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = POSTS_IN_PAGE
    ordering = '-pub_date'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        if self.user == self.request.user:
            return Post.objects.select_related(
                'category',
                'location',
                'author'
            ).filter(
                author=self.user
            ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return get_some_queryset().filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class PostDetailView(DetailView):
    """ Страница поста """
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        now = timezone.now()

        if (not post.is_published or (post.category
                                      and not post.category.is_published)):
            if (not request.user.is_authenticated
                    or request.user != post.author):
                raise Http404('Page not found')
            return super().dispatch(request, *args, **kwargs)

        if post.pub_date > now and request.user != post.author:
            raise Http404('Page not found')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        post = self.object
        context['post'] = post
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.id_post_comment = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = Post.objects.get(pk=self.kwargs.get('post_id'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.id_post_comment.pk})


class CommentUpdateView(AuthorshipMixin, ScuccesUrlPostDetail, UpdateView):
    form_class = CommentForm
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post,
                                            pk=self.kwargs['post_id'])
        context['comment'] = get_object_or_404(Comment,
                                               pk=self.kwargs['comment_id'])
        return context


class PostUpdateView(AuthorshipMixin, UpdateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )


class UpdateProfile(LoginRequiredMixin, UpdateView):
    queryset = Post.objects.select_related()
    form_class = EditUserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )


class PostDeleteView(AuthorshipMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user}
        )


class CommentDeleteView(AuthorshipMixin, ScuccesUrlPostDetail, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'
