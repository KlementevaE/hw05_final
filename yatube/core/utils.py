from django.core.paginator import Paginator


def page(request, post_list):
    COUNT_POST = 10
    paginator = Paginator(post_list, COUNT_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
