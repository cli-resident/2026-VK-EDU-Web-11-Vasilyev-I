from django.http import HttpRequest


def sidebar(request: HttpRequest) -> dict[str, list[str]]:
    return {
        'popular_tags': ['python', 'django', 'javascript', 'bootstrap', 'web', 'css', 'html', 'postgresql'],
        'best_members': ['Иван Васильев', 'Анна Смирнова', 'Алексей Петров', 'Мария Иванова', 'Дмитрий Соколов'],
    }
