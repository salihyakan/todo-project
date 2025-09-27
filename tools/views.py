from django.shortcuts import render

def tools_home(request):
    return render(request, 'tools/home.html')

def calculator(request):
    return render(request, 'tools/calculator.html')

def stopwatch(request):
    return render(request, 'tools/stopwatch.html')

def timer(request):
    return render(request, 'tools/timer.html')