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


def get_parents(struct):
    """Формирование списка родительских запросов"""

    parents = struct.get_ancestors(include_self=False)

    # Подзапрос для получения последней статьи для каждого struct
    latest_article = Article.objects.filter(struct=OuterRef("pk")).order_by("-date")

    # Основной запрос
    result = parents.annotate(
        article_title=Subquery(latest_article.values("title")[:1]),
    ).values("id", "article_title")

    return result


def get_breadcrumbs(struct):
    breadcrumbs = [[reverse("app_wiki:root"), "app_wiki"]]
    parents = get_parents(struct)
    if len(parents) > 1:
        for parent in parents[1:]:
            breadcrumbs.append(
                [
                    reverse("app_wiki:view", args=[parent["id"]]),
                    parent["article_title"],
                ]
            )
    return breadcrumbs
