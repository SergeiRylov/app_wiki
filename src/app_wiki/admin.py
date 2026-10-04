from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from app_wiki.models import Article, File, Image, Struct


class ArticleTabAdmin(admin.TabularInline):
    model = Article
    list_display = ("date", "user", "title")
    extra = 0


@admin.register(Struct)
class StructAdmin(MPTTModelAdmin):
    list_display = ("id", "last_article_title", "is_active")
    inlines = (ArticleTabAdmin,)

    def get_queryset(self, request):
        # Оптимизация: подтягиваем статьи одним запросом
        qs = super().get_queryset(request)
        return qs.prefetch_related("article_set")

    @admin.display(description="Последняя статья")
    def last_article_title(self, obj):
        article = obj.article_set.order_by("-date").first()
        return article.title if article else "—"


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "article", "file")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "article", "file")
