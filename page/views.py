from django.shortcuts import render

# Create your views here.

def home_page_view(request):
    context =  {}
    return render(request, 'page/home_page.html', context)


def calendar_view(request):
    context = {}
    return render(request, 'page/calendar.html',context)


def tasks_view(request):
    context = {}
    return render(request, 'page/tasks.html', context)


def user_home_page_view(request):
    context = {}
    return render(request, 'page/user_home_page.html', context)


def user_task_add_view(request):
    context = {}
    return render(request, 'page/user_task_add.html', context)

