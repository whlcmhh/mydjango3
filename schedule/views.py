from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from schedule.models  import sch
from schedule.serializers import schSerializer

# Create your views here.

def index(request):
    return render(request, 'index.html')

def add(request):
    a=request.GET.get('a',1)
    b=request.GET.get('b',2)
    c=int(a)+int(b)
    return HttpResponse(str(c))

def sche(request):
    sch_list=sch.objects.all()
    # sch_list_json=serializers.serialize('json',sch_list)
    # return HttpResponse(sch_list_json)
    sch_list_json=schSerializer(sch_list,many=True)
    return JsonResponse(sch_list_json.data,safe=False)