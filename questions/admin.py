from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ['author']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'created_at']
    search_fields = ['title', 'text', 'author__username']
    list_filter = ['created_at']
    list_select_related = ['author']
    raw_id_fields = ['author', 'tags']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'author', 'rating', 'correct']
    search_fields = ['text', 'author__username', 'question__title']
    list_filter = ['correct', 'created_at']
    list_select_related = ['author', 'question']
    raw_id_fields = ['author', 'question']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'questions_count']
    search_fields = ['name']
    list_filter = ['questions_count']


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'value']
    search_fields = ['user__username', 'question__title']
    list_filter = ['value']
    list_select_related = ['user', 'question']
    raw_id_fields = ['user', 'question']


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'value']
    search_fields = ['user__username', 'answer__text']
    list_filter = ['value']
    list_select_related = ['user', 'answer']
    raw_id_fields = ['user', 'answer']
