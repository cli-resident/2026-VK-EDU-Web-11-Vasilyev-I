from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, render

from core.pagination import paginate
from .models import Answer, Question, Tag
from .forms import AnswerForm, CorrectAnswerForm, QuestionForm, VoteForm


def index(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '').strip()
    questions = Question.objects.with_vote(request.user).newest().search(query)
    return render(request, 'questions/index.html', {'page': paginate(questions, request, 20), 'query': query})


def hot(request: HttpRequest) -> HttpResponse:
    return render(request, 'questions/hot.html', {'page': paginate(Question.objects.with_vote(request.user).best(), request, 20)})


def tag(request: HttpRequest, tag_name: str) -> HttpResponse:
    tag = get_object_or_404(Tag, name=tag_name)
    return render(request, 'questions/tag.html', {'page': paginate(Question.objects.with_vote(request.user).with_tag(tag), request, 20), 'tag_name': tag.name})


def question(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question.objects.with_vote(request.user).for_display(), pk=question_id)
    form = AnswerForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if form.is_valid():
            return redirect(form.save(request.user, question))
    return render(request, 'questions/question.html', {'question': question, 'page': paginate(Answer.objects.with_vote(request.user).for_question(question), request, 30), 'form': form})


@login_required
def ask(request: HttpRequest) -> HttpResponse:
    form = QuestionForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        return redirect(form.save(request.user))
    return render(request, 'questions/ask.html', {'form': form})


def vote(request, kind: str, target_id: int):
    if request.method != 'POST':
        return JsonResponse({'error': 'Нужен POST-запрос.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Войдите, чтобы голосовать.'}, status=401)
    model = Question if kind == 'question' else Answer
    target = model.objects.filter(pk=target_id).first()
    if target is None:
        return JsonResponse({'error': 'Объект не найден.'}, status=404)
    form = VoteForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': form.errors.as_text()}, status=400)
    return JsonResponse(form.save(request.user, target))


def correct_answer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Нужен POST-запрос.'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Войдите, чтобы выбрать ответ.'}, status=401)
    form = CorrectAnswerForm(request.POST, user=request.user)
    if not form.is_valid():
        return JsonResponse({'error': form.errors.as_text()}, status=400)
    return JsonResponse(form.save())
