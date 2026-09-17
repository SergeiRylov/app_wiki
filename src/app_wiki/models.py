from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Struct(MPTTModel):
    parent = TreeForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        verbose_name="Parents articles",
    )
    # slug = models.SlugField()
    sortorder = models.IntegerField(default=1000)

    class Meta:
        default_permissions = ()
        ordering = ("sortorder",)

    def __str__(self):
        return self.get_article().title

    def get_article(self):
        return Article.objects.filter(struct=self).last()

    def get_navigation(self):
        """
        Возвращает queryset для отрисовки текущего расположения статьи.
        """
        result = (
            Struct.objects.filter(tree_id=self.tree_id)
            .filter(
                Q(id=self.id)
                | Q(id__in=self.get_ancestors().values("id"))
                | Q(id__in=self.get_children().values("id"))
                | Q(id__in=self.get_siblings().values("id"))
                | Q(level__in=[0, 1]),
            )
            .distinct()
        )

        return result


class Article(models.Model):
    struct = models.ForeignKey(Struct, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="app_wiki_article_set",
    )
    title = models.CharField(max_length=1024, verbose_name=_("Title"))
    body = models.TextField(verbose_name=_("Content"), null=True, blank=True)
    changes = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("Changes"))

    class Meta:
        default_permissions = ()
        ordering = ("date", "id")

    def __str__(self):
        return self.title

    def copy(self, user=None):
        """Создание дубликата статьи"""
        self_id = self.id
        article = self
        article.pk = None
        article.user = user
        article.save()

        for image in Image.objects.filter(article_id=self_id):
            new = image
            new.pk = None
            new.article = article
            new.save()

        for file in File.objects.filter(article_id=self_id):
            new = file
            new.pk = None
            new.article = article
            new.save()

        return article


class Image(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="app_wiki_image_set",
    )
    description = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("Description"))
    file = models.ImageField(upload_to="app_wiki/%Y/%m/%d")

    class Meta:
        default_permissions = ()
        ordering = ("id",)


class File(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="app_wiki_file_set",
    )
    description = models.CharField(max_length=1024, null=True, blank=True, verbose_name=_("Description"))
    file = models.FileField(upload_to="app_wiki/%Y/%m/%d")

    class Meta:
        default_permissions = ()
        ordering = ("id",)
