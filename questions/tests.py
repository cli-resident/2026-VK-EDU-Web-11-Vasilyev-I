from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


@override_settings(DEBUG=False)
class PagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('ivan')
        Profile.objects.create(user=cls.user)
        cls.tag = Tag.objects.create(name='python')
        for number in range(25):
            question = Question.objects.create(title=f'Вопрос {number}', text='Текст вопроса', author=cls.user, rating=number)
            question.tags.add(cls.tag)

    def test_pagination_html(self):
        first = self.client.get('/')
        second = self.client.get('/', {'page': 2})
        self.assertEqual(len(first.context['page']), 20)
        self.assertEqual(len(second.context['page']), 5)
        for question in first.context['page']:
            self.assertContains(first, f'href="{question.get_absolute_url()}"')
            self.assertNotContains(second, f'href="{question.get_absolute_url()}"')

    def test_sorting_and_tag(self):
        response = self.client.get('/hot/')
        ratings = [question.rating for question in response.context['page']]
        self.assertGreater(len(ratings), 1)
        self.assertEqual(ratings, sorted(ratings, reverse=True))
        response = self.client.get('/tag/python/')
        self.assertTrue(response.context['page'].object_list)
        for question in response.context['page']:
            self.assertIn(self.tag, question.tags.all())

    def test_missing_and_empty(self):
        self.assertEqual(self.client.get('/question/999999/').status_code, 404)
        self.assertEqual(self.client.get('/tag/unknown/').status_code, 404)
        self.assertEqual(self.client.get('/question/abc/').status_code, 404)
        Question.objects.all().delete()
        self.assertContains(self.client.get('/'), 'Вопросов не найдено.')

    def test_invalid_pages(self):
        for value in ['abc', '-1', '0', '999999']:
            with self.subTest(value=value):
                self.assertEqual(self.client.get('/', {'page': value}).context['page'].number, 1)

    def test_queries_do_not_grow(self):
        with self.assertNumQueries(5):
            self.client.get('/')
        Question.objects.exclude(pk=Question.objects.first().pk).delete()
        with self.assertNumQueries(5):
            self.client.get('/')

    def test_vote_constraint(self):
        question = Question.objects.first()
        QuestionLike.objects.create(user=self.user, question=question, value=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            QuestionLike.objects.create(user=self.user, question=question, value=-1)


class FillTests(TestCase):
    def test_counts_and_repeat_run(self):
        for multiplier in [1, 2]:
            call_command('fill_db', 2, stdout=StringIO())
            self.assertEqual(User.objects.count(), 2 * multiplier)
            self.assertEqual(Profile.objects.count(), 2 * multiplier)
            self.assertEqual(Question.objects.count(), 20 * multiplier)
            self.assertEqual(Answer.objects.count(), 200 * multiplier)
            self.assertEqual(Tag.objects.count(), 2 * multiplier)
            self.assertEqual(QuestionLike.objects.count() + AnswerLike.objects.count(), 400 * multiplier)
