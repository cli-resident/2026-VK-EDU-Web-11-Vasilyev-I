from itertools import islice
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


def insert_batches(model, objects) -> list:
    iterator = iter(objects)
    ids = []
    while batch := list(islice(iterator, 2000)):
        created = model.objects.bulk_create(batch, batch_size=2000)
        ids.extend(item.pk for item in created)
    return ids


class Command(BaseCommand):
    help = 'Заполнить базу тестовыми данными.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    @transaction.atomic
    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio < 2:
            raise CommandError('Нужно хотя бы 2 пользователя для заданного числа уникальных оценок.')
        fake = Faker('ru_RU')
        prefix = uuid4().hex[:12]
        names = [fake.name() for _ in range(min(ratio, 1000))]
        sentences = [fake.sentence(nb_words=8) for _ in range(1000)]
        texts = [fake.paragraph(nb_sentences=3) for _ in range(1000)]
        users = insert_batches(User, (User(username=f'{prefix}_{number}', email=f'{prefix}_{number}@example.com', first_name=names[number % len(names)], password='!') for number in range(ratio)))
        insert_batches(Profile, (Profile(user_id=user_id) for user_id in users))
        tags = insert_batches(Tag, (Tag(name=f'{fake.word()[:25]}-{prefix}-{number}', questions_count=10) for number in range(ratio)))
        questions = insert_batches(Question, (Question(title=sentences[number % 1000], text=texts[number % 1000], author_id=users[number % ratio], rating=1, answers_count=10) for number in range(ratio * 10)))
        insert_batches(Question.tags.through, (Question.tags.through(question_id=question_id, tag_id=tags[number % ratio]) for number, question_id in enumerate(questions)))
        self.stdout.write('Пользователи, теги и вопросы добавлены.')
        answers = insert_batches(Answer, (Answer(question_id=questions[number // 10], author_id=users[number % ratio], text=texts[number % 1000], rating=2 if number < ratio * 90 else 1) for number in range(ratio * 100)))
        insert_batches(QuestionLike, (QuestionLike(user_id=users[number % ratio], question_id=question_id, value=1) for number, question_id in enumerate(questions)))
        insert_batches(AnswerLike, (AnswerLike(user_id=users[number % ratio], answer_id=answer_id, value=1) for number, answer_id in enumerate(answers)))
        insert_batches(AnswerLike, (AnswerLike(user_id=users[(number + 1) % ratio], answer_id=answer_id, value=1) for number, answer_id in enumerate(answers[:ratio * 90])))
        self.stdout.write(self.style.SUCCESS(f'Добавлено {ratio} пользователей и связанных данных.'))
