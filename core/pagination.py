from collections.abc import Sequence

from django.http import HttpRequest
from django.db.models import QuerySet
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator


def paginate(objects_list: Sequence | QuerySet, request: HttpRequest, per_page: int = 10) -> Page:
    paginator = Paginator(objects_list, per_page)
    number = request.GET.get('page', 1)

    try:
        page = paginator.page(number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(1)

    page.numbers = paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
    return page
