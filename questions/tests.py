from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from core.pagination import paginate
from .data import questions


class PagesTests(SimpleTestCase):
    def test_pages_open(self):
        pages = [('questions:index', []), ('questions:hot', []), ('questions:tag', ['python']), ('questions:question', [35]), ('questions:ask', []), ('core:login', []), ('core:signup', []), ('core:profile', [])]
        for name, args in pages:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'AskRu')

    def test_pages_have_different_questions(self):
        first = self.client.get(reverse('questions:index'))
        second = self.client.get(reverse('questions:index'), {'page': 2})
        first_ids = {question['id'] for question in first.context['page']}
        second_ids = {question['id'] for question in second.context['page']}
        self.assertEqual(len(first_ids), 10)
        self.assertFalse(first_ids & second_ids)

    def test_sorting(self):
        response = self.client.get(reverse('questions:hot'))
        ratings = [question['rating'] for question in response.context['page']]
        self.assertEqual(ratings, sorted(ratings, reverse=True))
        response = self.client.get(reverse('questions:index'))
        dates = [question['created_at'] for question in response.context['page']]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_tag_filter(self):
        response = self.client.get(reverse('questions:tag', args=['python']))
        for question in response.context['page']:
            self.assertIn('python', question['tags'])
        empty = self.client.get(reverse('questions:tag', args=['unknown']))
        self.assertContains(empty, 'Вопросов не найдено.')

    def test_question_and_answers(self):
        response = self.client.get(reverse('questions:question', args=[1]), {'page': 2})
        self.assertEqual(response.context['question']['id'], 1)
        self.assertEqual(response.context['page'].number, 2)
        self.assertEqual(len(response.context['page']), 10)
        for answer in response.context['page']:
            self.assertEqual(answer['question_id'], 1)
        self.assertEqual(self.client.get(reverse('questions:question', args=[9999])).status_code, 404)

    def test_search_keeps_query_in_pagination(self):
        response = self.client.get(reverse('questions:index'), {'q': 'шаблон'})
        self.assertContains(response, '&amp;q=')
        for question in response.context['page']:
            self.assertIn('шаблон', (question['title'] + question['text']).lower())


class PaginationTests(SimpleTestCase):
    def test_invalid_page_numbers(self):
        factory = RequestFactory()
        for value in ['abc', '0', '-1', '9999', '1.5', '']:
            with self.subTest(value=value):
                request = factory.get('/', {'page': value})
                self.assertEqual(paginate(questions, request).number, 1)

    def test_empty_list(self):
        page = paginate([], RequestFactory().get('/'))
        self.assertEqual(page.number, 1)
        self.assertEqual(list(page), [])

    def test_last_page(self):
        page = paginate(questions, RequestFactory().get('/', {'page': 7}))
        self.assertEqual(len(page), 5)
        self.assertFalse(page.has_next())
