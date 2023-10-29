from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма публикации"""

    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'location', 'category', 'pub_date')
        widgets = {'pub_date': forms.DateInput(
            format='%%d-%m-%Y %H:%M',
            attrs={'type': 'datetime-local'},
        ),
        }

    def clean(self):
        send_mail(
            subject='Тема',
            message='Текст',
            from_email='post_form@blogicum.not',
            recipient_list=['admin@blogicum.not'],
            fail_silently=True,
        )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class CommentForm(forms.ModelForm):
    """Форма добавления комментария"""

    class Meta:
        model = Comment
        fields = ('text',)


class EditUserForm(forms.ModelForm):
    """Форма редактирования профиля"""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
        )
