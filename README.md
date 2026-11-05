# AskRu

ДЗ2: Django, маршруты, шаблоны и пагинация. Данные хранятся в списках в `questions/data.py`, база пока не используется. Формы и голосование демонстрационные, изменения не сохраняются.

## Локальный запуск

Нужен Python 3.12 или новее.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python manage.py runserver
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py runserver
```

Открыть http://127.0.0.1:8000/. В `.env` задаются `SECRET_KEY`, `DEBUG` и `ALLOWED_HOSTS`. Для локального запуска достаточно настроек из примера. Миграции для ДЗ2 не нужны.

## Docker

Нужны Docker и Docker Compose. Скопировать `.env.example` в `.env`, затем:

```bash
docker compose up --build
```

Сайт доступен на http://localhost:8000/. Код подключён через volume, папка `media` хранится в отдельном volume. Остановить контейнеры: `docker compose down`.

## Страницы

| Адрес | Страница |
| --- | --- |
| `/` | Новые вопросы |
| `/hot/` | Популярные вопросы |
| `/tag/python/` | Вопросы по тегу |
| `/question/35/` | Вопрос и ответы |
| `/ask/` | Создание вопроса |
| `/login/` | Вход |
| `/signup/` | Регистрация |
| `/profile/` | Настройки профиля |

Пагинация: `/?page=2`. Для проверки ответов: `/question/1/?page=2`. Неверный номер заменяется первой страницей. Несуществующий вопрос возвращает 404. Поиск: `/?q=django`.

## Структура

- `application/` — настройки и корневые маршруты;
- `core/` — страницы пользователя, общий макет, статика и пагинация;
- `questions/` — страницы вопросов, данные и шаблоны карточек;
- `public/` — исходная статическая вёрстка ДЗ1;
- `static/` — результат `collectstatic`, не хранится в Git;
- `media/` — загруженные файлы, не хранится в Git.

## Проверка

```bash
python manage.py check
python manage.py test
```

В Windows без активации окружения использовать `.\.venv\Scripts\python` вместо `python`.
