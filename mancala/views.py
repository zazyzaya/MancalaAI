from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def result(request):
    result = request.GET['result']
    return render(request, 'result.html', {'result':result})