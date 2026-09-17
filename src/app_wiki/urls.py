from django.urls import include, path

from app_wiki.views import files, images, views

app_name = "app_wiki"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("search/modal/", views.search_modal, name="search-modal"),
    path("create/", views.create, name="create"),
    path(
        "<id_struct>/",
        include(
            [
                path(
                    "images/",
                    include(
                        [
                            path("<int:id_image>/", images.image_edit, name="images-edit"),
                            path("add/", images.image_add, name="images-add"),
                            path("", images.index, name="images-index"),
                        ]
                    ),
                ),
                path(
                    "files/",
                    include(
                        [
                            path("<int:id_file>/", files.edit, name="files-edit"),
                            path("add/", files.add, name="files-add"),
                            path("", files.index, name="files-index"),
                        ]
                    ),
                ),
                path("history/", views.history, name="history"),
                path("preview/", views.preview, name="preview"),
                path("edit/", views.edit, name="edit"),
                path("", views.details, name="view"),
            ]
        ),
    ),
    path("", views.root, name="root"),
]
