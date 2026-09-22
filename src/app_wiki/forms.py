from django import forms
from django.utils.translation import gettext_lazy as _

from app_wiki.models import Article, Struct


class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("title",)
        widgets = {
            "title": forms.TextInput(attrs={"required": True}),
        }
        labels = {
            "struct": _("Parent article"),
        }

    parent = forms.ChoiceField(label=_("Parent article"), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].choices = [
            (struct.pk, "{} {}".format("- " * struct.level, struct.get_article().title))
            for struct in Struct.objects.all()
        ]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("title", "body", "changes")
        widgets = (
            {
                "title": forms.TextInput(attrs={"required": True}),
                "body": forms.Textarea(attrs={"required": False, "class": "markdown-editor"}),
                "changes": forms.TextInput(attrs={"required": False}),
            },
        )
        help_texts = {
            "changes": "If field is empty, content will be created automatically",
        }


class AttachForm(forms.Form):
    description = forms.CharField(max_length=1024, required=False)


class SearchForm(forms.Form):
    search = forms.CharField()
