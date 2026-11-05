def sidebar(request):
    return {
        'popular_tags': ['python', 'django', 'javascript', 'bootstrap', 'web', 'css', 'html', 'postgresql'],
        'best_members': ['Иван Васильев', 'Анна Смирнова', 'Алексей Петров', 'Мария Иванова', 'Дмитрий Соколов'],
    }
