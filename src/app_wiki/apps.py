from django.apps import AppConfig


class app_wikiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_wiki"          # путь импорта пакета
    label = "app_wiki"         # app_label (важно для миграций)
    verbose_name = "Simple Wiki"