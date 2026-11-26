# AskRu

Учебный сайт вопросов и ответов на Django и PostgreSQL.

## Локальный запуск

Нужны Python 3.12 и PostgreSQL 17. Создайте базу askru и пользователя с доступом к ней.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env.local
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Перед миграциями заполните в .env.local параметры своей базы и SECRET_KEY. Для тестов пользователь PostgreSQL должен иметь право CREATEDB.

## Docker Compose

Скопируйте .env.example в .env.docker, задайте пароль и SECRET_KEY. Для контейнера укажите DB_HOST=db и DB_PORT=5432.

```sh
docker compose --env-file .env.docker up --build
docker compose --env-file .env.docker exec web python manage.py createsuperuser
```

Миграции выполняются при запуске web. Данные БД и аватары сохраняются в volumes. Файлы окружения не коммитятся.

## Тестовые данные

```sh
python manage.py fill_db 10001
```

Команда добавляет ratio пользователей и тегов, ratio * 10 вопросов, ratio * 100 ответов и ratio * 200 оценок. Использует Faker и bulk_create пакетами. Повторный запуск добавляет новую порцию. Минимальный ratio равен 2, иначе невозможно создать заданное число уникальных голосов. У тестовых пользователей отключён пароль.

## Страницы

- / - новые вопросы, поиск через q
- /hot/ - популярные вопросы
- /tag/<имя>/ - вопросы по тегу
- /question/<id>/ - вопрос и ответы
- /login/, /signup/, /profile/, /ask/ - формы
- /admin/ - административная панель

Вопросы разбиты по 20, ответы по 30. Неизвестные объекты возвращают 404, неверный номер страницы заменяется на 1. В ДЗ 4 работают регистрация, вход, выход, профиль, публикация вопросов и ответов. Голосование и выбор правильного ответа выполняются через AJAX с CSRF. Изменять профиль можно только свой, правильный ответ выбирает автор вопроса. Аватары: JPG, PNG и WebP до 5 МБ, имена файлов случайные. После ответа открывается нужная страница с якорем.

```sh
python manage.py test
```

Debug toolbar подключается только при DEBUG=True. Данные выбираются с select_related и prefetch_related. Исходная верстка ДЗ 1 находится в public.
