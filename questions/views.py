from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from core.pagination import paginate
from .data import answers, questions


def index(request: HttpRequest) -> HttpResponse:
    question_list = sorted(questions, key=lambda question: question['created_at'], reverse=True)
    query = request.GET.get('q', '').strip()
    if query:
        question_list = [question for question in question_list if query.lower() in (question['title'] + question['text']).lower()]
    return render(request, 'questions/index.html', {'page': paginate(question_list, request), 'query': query})


def hot(request: HttpRequest) -> HttpResponse:
    question_list = sorted(questions, key=lambda question: question['rating'], reverse=True)
    return render(request, 'questions/hot.html', {'page': paginate(question_list, request)})


def tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    question_list = [question for question in questions if tag_name in question['tags']]
    question_list.sort(key=lambda question: question['rating'], reverse=True)
    return render(request, 'questions/tag.html', {'page': paginate(question_list, request), 'tag_name': tag_name})


def question(request: HttpRequest, question_id: int) -> HttpResponse:
    current_question = None
    for candidate in questions:
        if candidate['id'] == question_id:
            current_question = candidate
            break
    if current_question is None:
        raise Http404('Вопрос не найден')

    answer_list = [answer for answer in answers if answer['question_id'] == question_id]
    answer_list.sort(key=lambda answer: (-answer['rating'], answer['created_at']))
    return render(request, 'questions/question.html', {'question': current_question, 'page': paginate(answer_list, request)})


def ask(request: HttpRequest) -> HttpResponse:
    return render(request, 'questions/ask.html')
