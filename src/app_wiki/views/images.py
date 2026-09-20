from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from app_wiki import forms
from app_wiki.models import Article, Image, Struct
from app_wiki.views import functions

TITLE = "app_wiki"


def index(request, id_struct):

    struct = get_object_or_404(Struct, id=id_struct)
    article = Article.objects.filter(struct=struct).last()

    content = {
        "title": article.title,
        "breadcrumbs": functions.get_breadcrumbs(struct),
        "struct": struct,
        "article": article,
    }
    return render(request, "app_wiki/images/index.html", content)


def image_add(request, id_struct):
    """Добавление фотографии"""

    struct = get_object_or_404(Struct, id=id_struct)
    old_article = Article.objects.filter(struct=struct).last()

    if request.POST:
        form = forms.AttachForm(request.POST)
        if form.is_valid():
            files = request.FILES.getlist("files")
            if files:
                article = old_article.copy(user=request.user)
                article.changes = _("Image(s) added")
                article.save()
                for fl in files:
                    image = Image.objects.create(
                        user=request.user, article=article, file=fl
                    )
                    if form.cleaned_data["description"]:
                        image.description = form.cleaned_data["description"]
                    image.save()

        return redirect(request.META["HTTP_REFERER"])
    else:
        form = forms.AttachForm()

    content = {"struct": struct, "form": form}
    return render(request, "app_wiki/images/modal-add.html", content)


def image_edit(request, id_struct, id_image):
    """Редактирование фотографии"""

    struct = get_object_or_404(Struct, id=id_struct)
    image = get_object_or_404(Image, id=id_image)
    article = Article.objects.filter(struct=struct).last()

    if request.POST:
        if request.POST.get("submit") == "delete":
            new_article = article.copy(user=request.user)
            new_article.changes = _("Deleted Image")
            new_article.save()
            for img in Image.objects.filter(article=new_article):
                if img.file.path == image.file.path:
                    img.delete()
                    break
        else:
            form = forms.AttachForm(
                request.POST, initial={"description": image.description}
            )
            if form.is_valid() and form.changed_data:
                new_article = article.copy(user=request.user)
                new_article.changes = _("Changed image description")
                new_article.save()
                for img in Image.objects.filter(article=new_article):
                    if img.file.path == image.file.path:
                        img.description = form.cleaned_data["description"]
                        img.save()
                        break
        return redirect(request.META["HTTP_REFERER"])
    else:
        form = forms.AttachForm(initial={"description": image.description})

    content = {"struct": struct, "image": image, "form": form}
    return render(request, "app_wiki/images/modal-edit.html", content)
