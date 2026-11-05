from django.http import Http404
from django.shortcuts import render

from core.pagination import paginate
from .data import answers, questions


def index(request):
    items = sorted(questions, key=lambda question: question['created_at'], reverse=True)
    query = request.GET.get('q', '').strip()
    if query:
        items = [question for question in items if query.lower() in (question['title'] + question['text']).lower()]
    return render(request, 'questions/index.html', {'page': paginate(items, request), 'query': query})


def hot(request):
    items = sorted(questions, key=lambda question: question['rating'], reverse=True)
    return render(request, 'questions/hot.html', {'page': paginate(items, request)})


def tag(request, tag_name):
    items = [question for question in questions if tag_name in question['tags']]
    items.sort(key=lambda question: question['rating'], reverse=True)
    return render(request, 'questions/tag.html', {'page': paginate(items, request), 'tag_name': tag_name})


def question(request, question_id):
    item = None
    for entry in questions:
        if entry['id'] == question_id:
            item = entry
            break
    if item is None:
        raise Http404('Вопрос не найден')

    items = [answer for answer in answers if answer['question_id'] == question_id]
    items.sort(key=lambda answer: (-answer['rating'], answer['created_at']))
    return render(request, 'questions/question.html', {'question': item, 'page': paginate(items, request)})


def ask(request):
    return render(request, 'questions/ask.html')
