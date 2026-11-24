import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Название')),
                ('questions_count', models.PositiveIntegerField(db_index=True, default=0, verbose_name='Количество вопросов')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150, verbose_name='Заголовок')),
                ('text', models.TextField(max_length=5000, verbose_name='Текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('rating', models.IntegerField(default=0, verbose_name='Рейтинг')),
                ('answers_count', models.PositiveIntegerField(default=0, verbose_name='Количество ответов')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('tags', models.ManyToManyField(related_name='questions', to='questions.tag', verbose_name='Теги')),
            ],
            options={
                'verbose_name': 'Вопрос',
                'verbose_name_plural': 'Вопросы',
            },
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=5000, verbose_name='Текст')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('rating', models.IntegerField(default=0, verbose_name='Рейтинг')),
                ('correct', models.BooleanField(default=False, verbose_name='Правильный ответ')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='questions.question', verbose_name='Вопрос')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='QuestionLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(-1, 'Дизлайк'), (1, 'Лайк')], verbose_name='Оценка')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='questions.question', verbose_name='Вопрос')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка вопроса',
                'verbose_name_plural': 'Оценки вопросов',
            },
        ),
        migrations.CreateModel(
            name='AnswerLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(-1, 'Дизлайк'), (1, 'Лайк')], verbose_name='Оценка')),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='questions.answer', verbose_name='Ответ')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Оценка ответа',
                'verbose_name_plural': 'Оценки ответов',
                'constraints': [models.UniqueConstraint(fields=('user', 'answer'), name='unique_answer_vote'), models.CheckConstraint(condition=models.Q(('value__in', [-1, 1])), name='valid_answer_vote')],
            },
        ),
        migrations.AddIndex(
            model_name='answer',
            index=models.Index(fields=['question', '-rating', 'created_at', 'id'], name='questions_a_questio_a1cb27_idx'),
        ),
        migrations.AddConstraint(
            model_name='answer',
            constraint=models.UniqueConstraint(condition=models.Q(('correct', True)), fields=('question',), name='one_correct_answer'),
        ),
        migrations.AddConstraint(
            model_name='questionlike',
            constraint=models.UniqueConstraint(fields=('user', 'question'), name='unique_question_vote'),
        ),
        migrations.AddConstraint(
            model_name='questionlike',
            constraint=models.CheckConstraint(condition=models.Q(('value__in', [-1, 1])), name='valid_question_vote'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['-created_at', '-id'], name='questions_q_created_79cadc_idx'),
        ),
        migrations.AddIndex(
            model_name='question',
            index=models.Index(fields=['-rating', '-id'], name='questions_q_rating_84e850_idx'),
        ),
    ]
