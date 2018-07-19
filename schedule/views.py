from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from schedule.models  import products,productsSerializers,dutygroups,dutygroupsSerializers,persons,personsSerializers
# from schedule.serializers import schSerializer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt


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

@api_view(['GET','POST'])
def products_list(request):
    if request.method == 'GET' :
        products_list=products.objects.all()
        products_list_json=productsSerializers(products_list,many=True)
        return JsonResponse(products_list_json.data,safe=False)
    elif request.method == 'POST' :
        serializer=productsSerializers(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)


@api_view(['GET','PUT','DELETE'])
def products_detail(request,pk):

    try:
        product=products.objects.get(pk=pk)
    except products.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET' :
        serializer=productsSerializers(product)
        return JsonResponse(serializer.data,status=200)

    if request.method == 'PUT' :
        serializer=productsSerializers(product,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)

    if request.method == 'DELETE':
        product.delete()
        return HttpResponse(status=204)

@api_view(['GET','POST'])
def dutygroups_list(request):
    if request.method == 'GET' :
        productname=request.GET.get('productname')
        product=dutygroups.objects.filter(productname=productname)
        serializer=dutygroupsSerializers(product)
        return JsonResponse(serializer.data,status=200)
    if request.method == 'POST' :
        serializer=dutygroupsSerializers(data=request.data)
        print(serializer)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)
        else:
            return HttpResponse(status=404)


@api_view(['GET','PUT','DELETE'])
def dutygroups_detail(request,pk):
    try :
        dutygroup=dutygroups.objects.get(pk=pk)
    except dutygroups.DoesNotExist :
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer=dutygroupsSerializers(dutygroup)
        return JsonResponse(serializer.data,status=200)
    if request.method == 'PUT':
        serializer=dutygroupsSerializers(dutygroup,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
    if request.method == 'DELETE':
        dutygroup.delete()
        return HttpResponse(status=204)















