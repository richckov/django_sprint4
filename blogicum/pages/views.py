from django.shortcuts import render


def csrf_failure(request, reason='Незащищенная форма'):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def something_wrong_with_server(request):
    return render(request, 'pages/500.html', status=500)
