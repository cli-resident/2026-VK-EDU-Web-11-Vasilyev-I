from django.http import HttpRequest

from .models import Profile
from questions.models import Tag


def sidebar(request: HttpRequest) -> dict:
    return {
        'popular_tags': Tag.objects.order_by('-questions_count', 'name')[:20],
        'best_members': Profile.objects.select_related('user').order_by('-rating', 'id')[:10],
    }
