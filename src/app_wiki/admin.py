from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from app_wiki.models import Article, File, Image, Struct


class ArticleTabAdmin(admin.TabularInline):
    model = Article
    list_display = ("date", "user", "title")
    extra = 0


@admin.register(Struct)
class StructAdmin(MPTTModelAdmin):
    inlines = (ArticleTabAdmin,)


# @admin.register(Article)
# class ArticleAdmin(admin.ModelAdmin):
#     list_display = ("date", "user", "struct__id", "title")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "article", "file")


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "article", "file")
