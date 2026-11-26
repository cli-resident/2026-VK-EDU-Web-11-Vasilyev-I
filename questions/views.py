from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from core.pagination import paginate
from .models import Answer, Question, Tag


def index(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '').strip()
    questions = Question.objects.newest().search(query)
    return render(request, 'questions/index.html', {'page': paginate(questions, request, 20), 'query': query})


def hot(request: HttpRequest) -> HttpResponse:
    return render(request, 'questions/hot.html', {'page': paginate(Question.objects.best(), request, 20)})


def tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    tag = get_object_or_404(Tag, name=tag_name)
    return render(request, 'questions/tag.html', {'page': paginate(Question.objects.with_tag(tag), request, 20), 'tag_name': tag.name})


def question(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question.objects.for_display(), pk=question_id)
    answers = Answer.objects.for_question(question)
    return render(request, 'questions/question.html', {'question': question, 'page': paginate(answers, request, 30)})


def ask(request: HttpRequest) -> HttpResponse:
    return render(request, 'questions/ask.html')
