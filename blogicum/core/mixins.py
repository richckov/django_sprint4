"""Файл для хранения собственны миксинов."""
from django.shortcuts import redirect
from django.urls import reverse


class AuthorshipMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class ScuccesUrlPostDetail:
    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']},
        )
