from datetime import datetime, timedelta


authors = [
    {'name': 'Иван Васильев', 'avatar': 'core/img/avatar-0.svg'},
    {'name': 'Анна Смирнова', 'avatar': 'core/img/avatar-1.svg'},
    {'name': 'Алексей Петров', 'avatar': 'core/img/avatar-2.svg'},
]

topics = [
    ('Как верифицировать аккаунт anthropic?', 'я сидел вайбкодил трекер привычек, но мне прилетела верификация, что делать?', ['web', 'python']),
    ('Как подключить CSS в Django?', 'Шаблон открывается, но стили не применяются. Где нужно хранить файлы?', ['django', 'css']),
    ('Как передать данные в шаблон?', 'Есть список словарей с вопросами. Как вывести их в HTML?', ['python', 'django']),
    ('Как сделать две колонки в Bootstrap?', 'На компьютере нужны две колонки, а на телефоне одна.', ['bootstrap', 'html']),
    ('Почему обработчик срабатывает дважды?', 'По одному нажатию на кнопку счётчик увеличивается на два.', ['javascript', 'web']),
    ('Как отсортировать вопросы по рейтингу?', 'Нужно сначала показывать вопросы с самым большим рейтингом.', ['python', 'postgresql']),
]

questions = []
for i in range(1, 66):
    title, text, tags = topics[(i - 1) % len(topics)]
    questions.append({
        'id': i,
        'title': title,
        'text': text,
        'tags': tags,
        'author': authors[(i - 1) % len(authors)],
        'rating': (i * 7) % 31,
        'created_at': datetime(2026, 11, 6, 12) - timedelta(hours=i),
        'answers_count': 35 if i == 1 else i % 5 + 1,
    })

answers = []
for question in questions:
    for i in range(question['answers_count']):
        answers.append({
            'id': len(answers) + 1,
            'question_id': question['id'],
            'text': 'Что именно не получается? Пришли подробности.' if i % 2 == 0 else 'У меня была похожая проблема. Напиши, что уже пробовал.',
            'author': authors[(i + 1) % len(authors)],
            'rating': question['answers_count'] - i,
            'created_at': question['created_at'] + timedelta(minutes=i + 1),
            'correct': i == 0,
        })
