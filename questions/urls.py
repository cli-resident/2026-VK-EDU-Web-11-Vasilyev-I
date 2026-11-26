from django.urls import path

from . import views


app_name = 'questions'
urlpatterns = [
    path('vote/question/<int:target_id>/', views.vote, {'kind': 'question'}, name='question_vote'),
    path('vote/answer/<int:target_id>/', views.vote, {'kind': 'answer'}, name='answer_vote'),
    path('answer/correct/', views.correct_answer, name='correct_answer'),
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
]
