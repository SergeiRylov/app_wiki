from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from app_wiki import forms
from app_wiki.models import Article, File, Struct
from app_wiki.views import functions

TITLE = "app_wiki"


def index(request, id_struct):

    struct = get_object_or_404(Struct, id=id_struct)
    article = Article.objects.filter(struct=struct).last()

    children = functions.get_children(struct)

    content = {
        "title": article.title,
        "breadcrumbs": functions.get_breadcrumbs(struct),
        "struct": struct,
        "children": children,
        "article": article,
    }
    return render(request, "app_wiki/files/index.html", content)


def add(request, id_struct):
    """Добавление фотографии"""

    struct = get_object_or_404(Struct, id=id_struct)
    old_article = Article.objects.filter(struct=struct).last()

    if request.POST:
        form = forms.AttachForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist("files")
            if files:
                article = old_article.copy(user=request.user)
                article.changes = _("File(s) added")
                article.save()
                for fl in files:
                    file = File.objects.create(article=article, file=fl)
                    if form.cleaned_data["description"]:
                        file.description = form.cleaned_data["description"]
                        file.save()

        return redirect(request.META["HTTP_REFERER"])
    else:
        form = forms.AttachForm()

    content = {"struct": struct, "form": form}
    return render(request, "app_wiki/files/modal-add.html", content)


def edit(request, id_struct, id_file):
    """Редактирование фотографии"""

    struct = get_object_or_404(Struct, id=id_struct)
    file = get_object_or_404(File, id=id_file)
    article = Article.objects.filter(struct=struct).last()

    if request.POST:
        if request.POST.get("submit") == "delete":
            new_article = article.copy(user=request.user)
            new_article.changes = _("Deleted File")
            new_article.save()
            for fl in File.objects.filter(article=new_article):
                if fl.file.path == file.file.path:
                    fl.delete()
                    break
        else:
            form = forms.AttachForm(request.POST, initial={"description": file.description})
            if form.is_valid() and form.changed_data:
                new_article = article.copy(user=request.user)
                new_article.changes = _("Changed file description")
                new_article.save()
                for fl in File.objects.filter(article=new_article):
                    if fl.file.path == file.file.path:
                        fl.description = form.cleaned_data["description"]
                        fl.save()
                        break
        return redirect(request.META["HTTP_REFERER"])
    else:
        form = forms.AttachForm(initial={"description": file.description})

    content = {"struct": struct, "file": file, "form": form}
    return render(request, "app_wiki/files/modal-edit.html", content)
