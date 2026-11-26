from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse


class Tag(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    questions_count = models.PositiveIntegerField('Количество вопросов', default=0, db_index=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class QuestionQuerySet(models.QuerySet):
    def for_display(self):
        return self.select_related('author__profile').prefetch_related('tags')

    def newest(self):
        return self.for_display().order_by('-created_at', '-id')

    def best(self):
        return self.for_display().order_by('-rating', '-id')

    def with_tag(self, tag: Tag):
        return self.best().filter(tags=tag)

    def search(self, query: str):
        return self.filter(Q(title__icontains=query) | Q(text__icontains=query)) if query else self


class Question(models.Model):
    title = models.CharField('Заголовок', max_length=150)
    text = models.TextField('Текст', max_length=5000)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор', related_name='questions')
    tags = models.ManyToManyField(Tag, verbose_name='Теги', related_name='questions')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    rating = models.IntegerField('Рейтинг', default=0)
    answers_count = models.PositiveIntegerField('Количество ответов', default=0)
    objects = QuestionQuerySet.as_manager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        indexes = [models.Index(fields=['-created_at', '-id']), models.Index(fields=['-rating', '-id'])]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse('questions:question', args=[self.pk])


class AnswerQuerySet(models.QuerySet):
    def for_question(self, question: Question):
        return self.filter(question=question).select_related('author__profile').order_by('-rating', 'created_at', 'id')


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    text = models.TextField('Текст', max_length=5000)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    rating = models.IntegerField('Рейтинг', default=0)
    correct = models.BooleanField('Правильный ответ', default=False)
    objects = AnswerQuerySet.as_manager()

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        indexes = [models.Index(fields=['question', '-rating', 'created_at', 'id'])]
        constraints = [models.UniqueConstraint(fields=['question'], condition=Q(correct=True), name='one_correct_answer')]

    def __str__(self) -> str:
        return self.text[:80]


class QuestionLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes', verbose_name='Вопрос')
    value = models.SmallIntegerField('Оценка', choices=[(-1, 'Дизлайк'), (1, 'Лайк')])

    class Meta:
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'
        constraints = [models.UniqueConstraint(fields=['user', 'question'], name='unique_question_vote'), models.CheckConstraint(condition=Q(value__in=[-1, 1]), name='valid_question_vote')]


class AnswerLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes', verbose_name='Ответ')
    value = models.SmallIntegerField('Оценка', choices=[(-1, 'Дизлайк'), (1, 'Лайк')])

    class Meta:
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'
        constraints = [models.UniqueConstraint(fields=['user', 'answer'], name='unique_answer_vote'), models.CheckConstraint(condition=Q(value__in=[-1, 1]), name='valid_answer_vote')]
