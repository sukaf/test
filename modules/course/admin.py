from django.contrib import admin
from .models import Article, Category, Comment, Cart,\
    ArticleVariation
from mptt.admin import DraggableMPTTAdmin


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    """
    Админ-панель модели категорий
    """
    list_display = ('tree_actions', 'indented_title', 'id', 'title', 'slug')
    list_display_links = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Основная информация', {'fields': ('title', 'slug', 'parent')}),
        ('Описание', {'fields': ('description',)})
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'time_create', 'teacher')
    list_filter = ('status', 'time_create', 'teacher')
    search_fields = ('title', 'short_description', 'full_description')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['teacher']


@admin.register(Comment)
class CommentAdminPage(DraggableMPTTAdmin):
    """
    Админ-панель модели комментариев
    """
    list_display = ('tree_actions', 'indented_title', 'article', 'author', 'time_create', 'status')
    mptt_level_indent = 2
    list_display_links = ('article',)
    list_filter = ('time_create', 'time_update', 'author')
    list_editable = ('status',)


admin.site.register(Cart)


class ArticleVariationInline(admin.TabularInline):
    model = ArticleVariation
    extra = 1


@admin.register(ArticleVariation)
class ArticleVariationAdmin(admin.ModelAdmin):
    list_display = ('article', 'name', 'price')
