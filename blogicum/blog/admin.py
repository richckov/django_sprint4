from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at',
    )
    list_editable = (
        # 'is_published',
        # 'category',
    )
    search_fields = (
        'title',
        'category',
    )
    list_display_links = ('title',)
    empty_value_display = 'Не задано'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'image',
        # 'small_image',
    )
    list_editable = (
        'category',
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)
    empty_value_display = 'Не задано'

    # @admin.display(description='Картинка')
    # def small_img(self, obj):
    #     if obj.image:
    #         return mark_safe(f
    # '<img scr={obj.image.url} width="80" height="60">')
