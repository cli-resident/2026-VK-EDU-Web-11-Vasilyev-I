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


class FormsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user('owner', password='Good-password-913')
        self.other = User.objects.create_user('other', password='Good-password-913')
        Profile.objects.create(user=self.owner)
        Profile.objects.create(user=self.other)
        self.question = Question.objects.create(title='Вопрос', text='Текст', author=self.owner)
        self.answer = Answer.objects.create(question=self.question, author=self.other, text='Ответ')

    def test_question_and_answer(self):
        self.assertEqual(self.client.get('/ask/').status_code, 302)
        self.client.force_login(self.owner)
        response = self.client.post('/ask/', {'title': 'Новый вопрос', 'text': 'Подробности', 'tags': 'python, django, css, html'})
        self.assertTrue(response.context['form'].errors)
        response = self.client.post('/ask/', {'title': 'Новый вопрос', 'text': 'Подробности', 'tags': 'python, django'})
        created = Question.objects.get(title='Новый вопрос')
        self.assertRedirects(response, created.get_absolute_url())
        self.assertEqual(created.tags.count(), 2)
        Answer.objects.bulk_create([Answer(question=self.question, author=self.owner, text='Старый ответ', rating=1) for _ in range(31)])
        response = self.client.post(self.question.get_absolute_url(), {'text': 'Последний ответ'})
        answer = Answer.objects.get(text='Последний ответ')
        self.assertRedirects(response, answer.get_absolute_url())
        self.assertIn('?page=2#answer-', response.url)

    def test_votes_and_permissions(self):
        url = f'/vote/question/{self.question.pk}/'
        self.assertEqual(self.client.post(url, {'value': 1}).status_code, 401)
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, {'value': 7}).status_code, 400)
        for value, expected in [(1, 1), (1, 0), (-1, -1), (1, 1)]:
            self.assertEqual(self.client.post(url, {'value': value}).json()['rating'], expected)
        self.assertContains(self.client.get(self.question.get_absolute_url()), 'aria-pressed="true"')
        answer_url = f'/vote/answer/{self.answer.pk}/'
        self.assertEqual(self.client.post(answer_url, {'value': -1}).json()['rating'], -1)
        data = {'question_id': self.question.pk, 'answer_id': self.answer.pk}
        self.assertEqual(self.client.post('/answer/correct/', data).status_code, 400)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post('/answer/correct/', data).json()['answer_id'], self.answer.pk)
        second = Answer.objects.create(question=self.question, author=self.other, text='Второй')
        data['answer_id'] = second.pk
        self.client.post('/answer/correct/', data)
        self.assertEqual(Answer.objects.filter(question=self.question, correct=True).count(), 1)
        self.assertIsNone(self.client.post('/answer/correct/', data).json()['answer_id'])

    def test_csrf(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(f'/vote/question/{self.question.pk}/', {'value': 1}).status_code, 403)
