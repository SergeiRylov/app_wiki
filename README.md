# app_wiki

**simple wiki app** — Django‑приложение для вики, оформленное как отдельный pip‑пакет.

## 📋 Возможности

- Статьи (`Article`) с поддержкой иерархии через `django-mptt`.
- Изображения (`Image`), привязанные к статьям и пользователям.
- Интеграция с `django.contrib.admin` (включая `django-mptt-admin`).
- Namespace `app_wiki` для URL и шаблонов — не конфликтует с другими приложениями.
- Поддержка i18n (переводы в `locale/`).
- Настройки через `settings.app_wiki_*` с разумными значениями по умолчанию.

## 📦 Установка

### Из GitHub (рекомендуется)

В `requirements.txt` вашего проекта добавьте:

```txt
app_wiki @ git+https://github.com/SergeiRylov/app_base.git
app_wiki @ git+https://github.com/SergeiRylov/app_wiki.git
```

Затем:

```bash
pip install -r requirements.txt
```

## Быстрый старт

### 1. Добавьте приложение в `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Зависимости app_wiki
    "mptt",
    "django_mptt_admin",
    "app_base.apps.app_baseConfig",
    # Само приложение
    "app_wiki.apps.app_wikiConfig",
]
```

### 2. Подключите URL

В корневом `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path("app_wiki/", include("app_wiki.urls")),
]
```

### 3. Примените миграции

```bash
python manage.py migrate
```

### 4. Проверьте

```bash
python manage.py check
```

Откройте `/app_wiki/` в браузере.



## Локализация

Переводы хранятся в `app_wiki/locale/`. Чтобы скомпилировать их после установки:

```bash
python manage.py compilemessages
```


## Лицензия

MIT. См. [LICENSE](LICENSE).