from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return render(request, 'index.html')

def add(request):
    a=request.GET.get('a',1)
    b=request.GET.get('b',2)
    c=int(a)+int(b)
    return HttpResponse(str(c))
