from django import forms
from django.db import transaction
from django.db.models import F, Q

from core.forms import StyledForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class QuestionForm(StyledForm, forms.ModelForm):
    tags = forms.CharField(label='Теги', max_length=152, help_text='До 3 тегов через запятую.')

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {'text': forms.Textarea(attrs={'rows': 7})}

    def clean_tags(self) -> list[str]:
        tags = list(dict.fromkeys(tag.strip().lower() for tag in self.cleaned_data['tags'].split(',') if tag.strip()))
        if not 1 <= len(tags) <= 3:
            raise forms.ValidationError('Укажите от 1 до 3 тегов.')
        if any(len(tag) > 50 or '/' in tag for tag in tags):
            raise forms.ValidationError('Тег должен быть не длиннее 50 символов и не содержать слеш.')
        return tags

    @transaction.atomic
    def save(self, author):
        question = super().save(commit=False)
        question.author = author
        question.save()
        tags = [Tag.objects.get_or_create(name=name)[0] for name in self.cleaned_data['tags']]
        question.tags.set(tags)
        Tag.objects.filter(pk__in=[tag.pk for tag in tags]).update(questions_count=F('questions_count') + 1)
        return question


class AnswerForm(StyledForm, forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 7})}

    @transaction.atomic
    def save(self, author, question):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        answer.save()
        Question.objects.filter(pk=question.pk).update(answers_count=F('answers_count') + 1)
        return answer


class VoteForm(forms.Form):
    value = forms.TypedChoiceField(choices=[(-1, 'Дизлайк'), (1, 'Лайк')], coerce=int)

    @transaction.atomic
    def save(self, user, target):
        target = type(target).objects.select_for_update().get(pk=target.pk)
        vote_model = QuestionLike if isinstance(target, Question) else AnswerLike
        relation = 'question' if isinstance(target, Question) else 'answer'
        votes = vote_model.objects.filter(user=user, **{relation: target})
        previous = votes.first()
        old_value = previous.value if previous else 0
        value = self.cleaned_data['value']
        new_value = 0 if old_value == value else value
        if new_value == 0:
            votes.delete()
        elif previous:
            votes.update(value=new_value)
        else:
            vote_model.objects.create(user=user, value=new_value, **{relation: target})
        target.rating += new_value - old_value
        target.save(update_fields=['rating'])
        return {'rating': target.rating, 'selected': new_value}


class CorrectAnswerForm(forms.Form):
    question_id = forms.IntegerField(min_value=1)
    answer_id = forms.IntegerField(min_value=1)

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        if 'question_id' not in data or 'answer_id' not in data:
            return data
        self.question = Question.objects.filter(pk=data['question_id']).first()
        if not self.question or self.question.author_id != self.user.pk:
            raise forms.ValidationError('Только автор вопроса может выбрать правильный ответ.')
        self.answer = Answer.objects.filter(pk=data['answer_id'], question=self.question).first()
        if not self.answer:
            raise forms.ValidationError('Ответ не найден у этого вопроса.')
        return data

    @transaction.atomic
    def save(self):
        Question.objects.select_for_update().get(pk=self.question.pk)
        answer = Answer.objects.get(pk=self.answer.pk)
        selected = not answer.correct
        Answer.objects.filter(question=self.question, correct=True).update(correct=False)
        if selected:
            Answer.objects.filter(pk=answer.pk).update(correct=True)
        return {'answer_id': answer.pk if selected else None}
