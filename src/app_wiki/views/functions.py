from django.db.models import OuterRef, Subquery
from django.urls import reverse

from app_wiki.models import Article, Struct

TITLE = "app_wiki"


def get_children(struct):
    """Формирование списка для статей раздела"""

    structs = Struct.objects.filter(parent=struct)

    # Запрос для получения последней статьи для каждого struct
    latest_article = Article.objects.filter(struct=OuterRef("pk")).order_by("-date")

    # Основной запрос
    result = structs.annotate(
        article_title=Subquery(latest_article.values("title")[:1]),
        # latest_article_date=Subquery(latest_article.values('date')[:1])
    ).values("id", "article_title")

    return result


def get_breadcrumbs(struct):
    breadcrumbs = []
    for parent in struct.get_ancestors(include_self=False):
        breadcrumbs.append(
            [
                reverse("app_wiki:view", args=[parent["id"]]),
                parent.get_article().title,
            ]
        )
    breadcrumbs.append([None, struct.get_article().title])
    return breadcrumbs
