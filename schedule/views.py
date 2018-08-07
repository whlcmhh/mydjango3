from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from schedule.serializers import products,productsSerializers,dutygroups,dutygroupsSerializers,persons,personsSerializers,dutygroupsDetailSerializers
# from schedule.serializers import schSerializer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,date,timedelta


@api_view(['GET','POST'])
def products_list(request):
    if request.method == 'GET' :
        products_list=products.objects.all()
        products_list_json=productsSerializers(products_list,many=True)
        return JsonResponse(products_list_json.data,safe=False)
    elif request.method == 'POST' :
        serializer=productsSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)
        else:
            return JsonResponse(serializer.errors)



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
        else:
            return JsonResponse(serializer.errors)

    if request.method == 'DELETE':
        product.delete()
        return HttpResponse(status=204)

@api_view(['GET','POST'])
def dutygroups_list(request):
    if request.method == 'GET' :
        productid=request.GET.get('productid')
        product=products.objects.get(id=productid).dutygroups_set.all()
        serializer=dutygroupsSerializers(product,many=True)
        return JsonResponse(serializer.data,status=200,safe=False)
    if request.method == 'POST' :
        serializer=dutygroupsSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)
        else:
            return JsonResponse(serializer.errors)


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
            return JsonResponse(serializer.data,status=201)
        else:
            return JsonResponse(serializer.errors)
    if request.method == 'DELETE':
        dutygroup.delete()
        return HttpResponse(status=204)

@api_view(['GET','POST'])
def dutypersons_list(request):
    if request.method == 'GET' :
        dutygroupid=request.GET.get('dutygroupid')
        # dutyperson=dutygroups.objects.get(id=dutygroupid).persons_groupname.all()
        dutyperson=persons.objects.filter(groupname=dutygroupid)
        serializer=personsSerializers(dutyperson,many=True)
        return JsonResponse(serializer.data,safe=False)
    if request.method == 'POST':
        serializer=personsSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        else:
            return  JsonResponse(serializer.errors)

@api_view(['GET','DELETE'])
def dutypersons_detail(request,pk):
    try:
        person=persons.objects.get(pk=pk)
    except persons.DoesNotExist :
        return HttpResponse(status=404)

    if request.method == 'GET' :
        serializer=personsSerializers(person)
        return JsonResponse(serializer.data,status=200)
    #修改值班组内人员的信息
    # if request.method == 'PUT' :
    #     serializer=personsSerializers(person,data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return JsonResponse(serializer.data,status=201)
    if request.method == 'DELETE' :
        person.delete()
        return HttpResponse(status=204)

@api_view(['GET',])#先把逻辑写完了再写pk
def dutylist(request,pk):
    if request.method == 'GET' :
        #查看pk是否存在
        if not dutygroups.objects.filter(productname=pk).exists():
            return JsonResponse({"msg":"dutygroup is null"})
        #值班表开始的日期选择，默认当前
        duty_date=request.GET.get('date')
        if duty_date is None:
            duty_date=datetime.now().date()
        else:
            duty_date=datetime.strptime(duty_date,'%Y-%m-%d').date()
        #查看当前生效的值班组
        if duty_date<dutygroups.objects.filter(productname=pk).only('startime').order_by('startime')[0].startime:
            return JsonResponse({"msg":"dutylist is null"})
        #最近的一个值班组的开始时间
        startime_last=dutygroups.objects.filter(startime__lt=duty_date,productname=pk).only('startime').order_by('-startime')[0].startime
        #当前时间和和最近一个值班组的开始时间时间差
        startime_differ=(duty_date-startime_last).days
        #时间差小于7天，直接返回最近的值班组
        if startime_differ<=7 :
            dutygroups_inturn_week_ob=dutygroups.objects.filter(productname=pk).order_by('-startime')[0]
            serializer=dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
            return JsonResponse(serializer.data,status=200)
        #时间差大于7天
        else:
            dutygruops_count=dutygroups.objects.filter(startime__lt=duty_date,productname=pk).count()
            startime_differ=startime_differ+7
            #轮到哪一周
            dutygroups_inturn_week=(startime_differ%(dutygruops_count*7))//7
            #轮到哪一天
            dutygroups_inturn_day=(startime_differ%(dutygruops_count*7))%7
            dutygroups_inturn_week_ob=dutygroups.objects.filter(startime__lt=duty_date,productname=pk).order_by('startime')[dutygroups_inturn_week]
            dutygroups_inturn_week_ob.startime=duty_date-timedelta(days=dutygroups_inturn_day)
            serializer=dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
            return JsonResponse(serializer.data,status=200)



















