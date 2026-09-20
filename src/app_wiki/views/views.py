import cmarkgfm
from django.core.paginator import Paginator
from django.db.models import OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from app_wiki import forms
from app_wiki.models import Article, Struct
from app_wiki.views import functions

TITLE = "app_wiki"


def root(request):
    """Начальная страница"""

    if not Struct.objects.exists():
        return render(request, "app_wiki/create_root.html")
    else:
        id_struct = Struct.objects.filter(parent=None).first().id
        return details(request, id_struct)


def create(request):
    """Создание статьи"""

    article = Article(user=request.user)
    initial = {"parent": request.GET.get("parent")}

    if request.POST:
        form = forms.ArticleCreateForm(request.POST, instance=article, initial=initial)
        if form.is_valid():
            struct = Struct.objects.create(parent_id=form.cleaned_data["parent"])
            article.struct = struct
            form.save()

            return redirect("app_wiki:view", struct.id)
    else:
        form = forms.ArticleCreateForm(instance=article, initial=initial)

    content = {"form": form}

    return render(request, "app_wiki/struct/modal-create.html", content)


def details(request, id_struct):

    struct = get_object_or_404(Struct, id=id_struct)
    article = Article.objects.filter(struct=struct).last()

    # text = markdown.markdown(article.body)
    # text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)
    article.body = cmarkgfm.github_flavored_markdown_to_html(article.body)

    content = {
        "title": article.title,
        "breadcrumbs": functions.get_breadcrumbs(struct),
        "struct": struct,
        "article": article,
    }
    return render(request, "app_wiki/details/index.html", content)


def edit(request, id_struct):
    """Редактирование статьи"""

    struct = get_object_or_404(Struct, id=id_struct)
    article = Article.objects.filter(struct=struct).last()
    initial = {"changes": ""}

    if request.POST:
        if request.POST.get("submit") == "delete":
            id_parent = struct.parent.id
            struct.delete()
            return redirect(reverse("app_wiki:view", id_parent))

        form = forms.ArticleForm(request.POST, instance=article)
        if form.is_valid() and form.changed_data:
            if "changes" in form.changed_data:
                changes = form.cleaned_data["changes"]
            elif "title" in form.changed_data and "body" in form.changed_data:
                changes = "Title and content was changed"
            elif "title" in form.changed_data:
                changes = "Title was changed"
            elif "body" in form.changed_data:
                changes = "Content was changed"
            else:
                changes = ""
            article = Article.objects.create(
                struct=struct, user=request.user, **form.cleaned_data
            )
            article.changes = changes
            article.save()
            return redirect(request.META["HTTP_REFERER"])
    else:
        form = forms.ArticleForm(instance=article, initial=initial)

    content = {
        "title": article.title,
        "breadcrumbs": functions.get_breadcrumbs(struct),
        "struct": struct,
        "form": form,
    }
    return render(request, "app_wiki/edit/index.html", content)


def preview(request):
    """Предпросмотр содержимого"""

    if request.POST:
        body = request.POST.get("body", "")
        # Преобразуем Markdown в HTML
        html_content = cmarkgfm.github_flavored_markdown_to_html(body)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"html": html_content})
        else:
            # Для обычного POST-запроса возвращаем страницу с предпросмотром
            context = {
                "preview_content": html_content,
                "title": request.POST.get("title", ""),
            }
            return render(request, "app_wiki_preview.html", context)


def history(request, id_struct):
    """Просмотр истории изменения статьи"""

    struct = get_object_or_404(Struct, id=id_struct)
    article = Article.objects.filter(struct=struct).last()

    content = {
        "title": article.title,
        "breadcrumbs": functions.get_breadcrumbs(struct),
        "struct": struct,
    }
    return render(request, "app_wiki/history/index.html", content)


def search(request):

    title = _("Search")
    breadcrumbs = (("/app_wiki/", TITLE), (None, title))

    search = request.GET.get("search", "")
    form = forms.SearchForm(initial={"search": search})

    results = []
    if search:
        latest_article = Article.objects.filter(struct=OuterRef("id")).order_by(
            "-date", "-id"
        )

        results = Struct.objects.annotate(
            latest_article_id=Subquery(latest_article.values("id")[:1]),
            latest_article_title=Subquery(
                Article.objects.filter(id=OuterRef("latest_article_id")).values(
                    "title"
                )[:1]
            ),
            latest_article_body=Subquery(
                Article.objects.filter(id=OuterRef("latest_article_id")).values("body")[
                    :1
                ]
            ),
            latest_article_date=Subquery(
                Article.objects.filter(id=OuterRef("latest_article_id")).values("date")[
                    :1
                ]
            ),
        ).filter(
            Q(latest_article_body__icontains=search)
            | Q(latest_article_title__icontains=search)
        )

        # Пагинация ДО постобработки — QuerySet остаётся ленивым,
        # count() и LIMIT/OFFSET выполняются на уровне БД.
        paginator = Paginator(results, 10)  # 10 записей на страницу
        page_number = request.GET.get("page")
        results = paginator.get_page(page_number)

        # Постобработка только для записей текущей страницы (максимум 10).
        search_lower = search.lower()
        for struct in results:
            body = struct.latest_article_body or ""

            # Ищем первую строку, содержащую поисковый запрос.
            matching_line = ""
            for line in body.splitlines():
                if search_lower in line.lower():
                    matching_line = line.strip()
                    break

            # Если в body ничего не нашли (совпадение было в title),
            # показываем первые 200 символов тела.
            if not matching_line and body:
                matching_line = body[:200].strip()
                if len(body) > 200:
                    matching_line += "..."

            struct.body_snippet = matching_line

    content = {
        "title": _("Search"),
        "breadcrumbs": breadcrumbs,
        "form": form,
        "results": results,
    }
    return render(request, "app_wiki/search/index.html", content)


def search_modal(request):

    if request.POST:
        form = forms.SearchForm(request.POST)
        if form.is_valid():
            url = "{}?search={}".format(
                reverse("app_wiki:search"), form.cleaned_data["search"]
            )
            return redirect(url)
    else:
        form = forms.SearchForm()

    content = {"form": form}
    return render(request, "app_wiki/search/modal-search.html", content)
