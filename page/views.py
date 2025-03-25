from django.contrib import messages
from django.shortcuts import render, redirect


# Create your views here.

def home_view(request):
    context =  {}
    return render(request, 'page/home.html', context)


def calendar_view(request):
    context = {}
    return render(request, 'page/calendar.html',context)


def tasks_view(request):
    context = {}
    return render(request, 'page/tasks.html', context)


def home_page_view(request):
    context = {}
    return render(request, 'page/home_page.html', context)


def task_add_view(request):
    context = {}
    return render(request, 'page/task_add.html', context)

