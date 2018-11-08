from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from schedule.serializers import productsSerializers,dutygroupsSerializers,personsSerializers,dutygroupsDetailSerializers,dutytmpSerializers,persondetailSerializers
from schedule.models import dutytmp,persondetail,persons,dutygroups,products
# from schedule.serializers import schSerializer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,date,timedelta
from django.db.models import F


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
        data=request.data
        if products.objects.get(id=data['productname']).dutymode == 'ops' :
            if dutygroups.objects.filter(productname=data['productname'], groupname=data['groupname']).exists():
                return JsonResponse({'msg': 'groupname must be unique'},status=500)
            if datetime.strptime(data['startime'],'%Y-%m-%d').date().weekday()<5 and data['worktime'] == 'weekend':
                return  JsonResponse({"msg":"date is not legal"},status=500)
            if datetime.strptime(data['startime'],'%Y-%m-%d').date().weekday()>4 and data['worktime'] == 'weekday' :
                return  JsonResponse({"msg":"date is not legal"},status=500)
            serializer=dutygroupsSerializers(data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data,safe=False,status=201)
            else:
                return JsonResponse(serializer.errors)
        data['startime']=datetime.strptime(data['startime'],'%Y-%m-%d').date()
        if dutygroups.objects.filter(productname=data['productname'],groupname=data['groupname']).exists():
            return JsonResponse({'msg':'groupname must be unique'},status=500)
        if products.objects.get(id=data['productname']).dutymode == 'week' :
            DUTY_CYCLE=7
        elif products.objects.get(id=data['productname']).dutymode == 'day':
            DUTY_CYCLE=1
        if dutygroups.objects.filter(productname=data['productname'],startime=data['startime']).exists():
            return JsonResponse({'msg':'date must be unique'},status=500)
        if not dutygroups.objects.filter(productname=data['productname']).exists():
            serializer=dutygroupsSerializers(data=data)
        else:
            loopcode=products.objects.get(id=data['productname']).loopcode
            if data['startime']<dutygroups.objects.filter(productname=data['productname']).order_by('startime')[loopcode].startime:
                products_object=products.objects.get(id=data['productname'])
                products_object.loopcode=loopcode+1
                products_object.save()
            serializer=dutygroupsSerializers(data=data)



        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)
        else:
            return JsonResponse(serializer.errors)

@api_view(['GET','PUT','DELETE'])
def dutygroups_detail(request,pk):
    try :
        dutygroup=dutygroups.objects.get(pk=pk)
        pid=products.objects.get(dutygroups__id=pk).id
    except dutygroups.DoesNotExist :
        return HttpResponse(status=404)
    if request.method == 'GET':
        serializer=dutygroupsSerializers(dutygroup)
        return JsonResponse(serializer.data,status=200)
    if request.method == 'PUT':
        data=request.data
        startime_old=dutygroup.startime
        startime_old_alter =0
        data['startime']=datetime.strptime(data['startime'],'%Y-%m-%d').date()
        if dutygroups.objects.filter(productname=data['productname'],groupname=data['groupname']).exclude(pk=pk).exists():
            return JsonResponse({'msg':'groupname must be unique'},status=500)
        if dutygroups.objects.filter(productname=data['productname'],startime=data['startime']).exists():
            return JsonResponse({"msg":"date already exits"},status=500)
        if products.objects.get(id=pid).dutymode == 'ops' :
            if data['startime'].weekday()<5 and data['worktime'] == 'weekend':
                return  JsonResponse({"msg":"date is not legal"},status=500)
            if data['startime'].weekday()>4 and data['worktime'] == 'weekday' :
                return  JsonResponse({"msg":"date is not legal"},status=500)
            serializer=dutygroupsSerializers(dutygroup,data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data,status=201)
            else:
                return JsonResponse(serializer.errors)
        serializer=dutygroupsSerializers(dutygroup,data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=201)
        else:
            return JsonResponse(serializer.errors)
    if request.method == 'DELETE':
        pid=dutygroups.objects.get(pk=pk).productname_id
        if products.objects.get(id=pid).dutymode == 'ops' :
            dutygroup.delete()
            return HttpResponse(status=204)
        product_object=products.objects.get(id=pid)
        loopcode=product_object.loopcode
        if dutygroup.startime<dutygroups.objects.filter(productname=pid).order_by('startime')[loopcode].startime:
            product_object.loopcode=loopcode-1
            product_object.save()
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
    if request.method == 'DELETE' :
        person.delete()
        return HttpResponse(status=204)

@api_view(['GET','POST'])
def persondetail_post(request):
    if request.method == 'GET':
        productid=request.GET.get('productid')
        persondetail_ob=persondetail.objects.filter(productname=productid)
        serializer=persondetailSerializers(persondetail_ob,many=True)
        return JsonResponse(serializer.data,status=200)
    if request.method == 'POST' :
        serializer=persondetailSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=200)
        else:
            return JsonResponse(serializer.errors,status=500)

@api_view(['GET','DELETE'])
def persondetail_delete(request,pk):
    try:
        persondetail_ob=persondetail.objects.get(id=pk)
    except persondetail_ob.DoesNotExist:
        return HttpResponse(status=404)
    if request.method == 'GET':
        serializer=persondetailSerializers(persondetail_ob)
        return JsonResponse(serializer.data,status=200)
    if request.method == 'DELETE' :
        persondetail_ob.delete()
        return HttpResponse(status=204)

@api_view(['GET',])
def dutylist(request,pk):
    if request.method == 'GET' :
        #查看pk是否存在
        # L=[]
        date_source=date(2018,1,1)
        if not dutygroups.objects.filter(productname=pk).exists():
            return JsonResponse([],safe=False)
        #值班表开始的日期选择，默认当前
        duty_date=request.GET.get('date')
        #没输入dutydate
        if duty_date is None:
            duty_date=datetime.now().date()
        #输入了dutydate，必须比now要大
        else:
            duty_date=datetime.strptime(duty_date,'%Y-%m-%d').date()
            if duty_date<datetime.now().date():
                return HttpResponse(status=500)
        #值班表时间长度,默认30天
        duty_len=request.GET.get('len')
        if duty_len is None:
            duty_len=31
        else:
            duty_len=int(duty_len)
        # 查看当前生效的值班组
        if duty_date + timedelta(days=duty_len) < dutygroups.objects.filter(productname=pk).only('startime').order_by('startime')[0].startime:
            return JsonResponse({"msg": "dutylist is null"})
        #运维值班模式
        if products.objects.get(id=pk).dutymode == 'ops' :
            List=[]
            i=0
            while(i<duty_len):
                if dutytmp.objects.filter(startime=duty_date, productname=pk).exists():
                    list_dutytmp_persons = []
                    for dutytmp_ob in dutytmp.objects.filter(startime=duty_date, productname=pk):
                        dict_dutytmp_person = {"personname": dutytmp_ob.personname}
                        list_dutytmp_persons.append(dict_dutytmp_person)
                    dict_dutytmp = {"productname": pk, "startime": duty_date,
                                    "persons_personname": list_dutytmp_persons}
                    List.append(dict_dutytmp)
                    i = i + 1
                    duty_date = duty_date + timedelta(days=1)
                    continue
                try:
                    if duty_date.weekday() < 5 :
                        startime_last=dutygroups.objects.filter(startime__lte=duty_date,productname=pk,worktime='weekday').order_by('-startime')[0].startime
                        dutygruops_count=dutygroups.objects.filter(startime__lte=duty_date,productname=pk,worktime='weekday').count()
                        startime_first = dutygroups.objects.filter(productname=pk, worktime='weekday').order_by('startime')[
                            0].startime
                    else:
                        startime_last = \
                        dutygroups.objects.filter(startime__lte=duty_date, productname=pk, worktime='weekend').order_by('-startime')[
                        0].startime
                        dutygruops_count=dutygroups.objects.filter(startime__lte=duty_date, productname=pk, worktime='weekend').count()
                        startime_first = dutygroups.objects.filter(productname=pk, worktime='weekend').order_by('startime')[0].startime
                except:
                    i = i + 1
                    duty_date = duty_date + timedelta(days=1)
                    continue
                if duty_date.weekday() < 5 :
                    startime_differ=(startime_last-startime_first).days-((startime_last-date_source).days//7-(startime_first-date_source).days//7)*2
                    dutydate_differ=(duty_date-startime_last).days-((duty_date-date_source).days//7-(startime_last-date_source).days//7)*2
                    worktime='weekday'
                else:
                    startime_differ=(startime_last-startime_first).days-((startime_last-date_source).days//7-(startime_first-date_source).days//7)*5
                    dutydate_differ=(duty_date-startime_last).days-((duty_date-date_source).days//7-(startime_last-date_source).days//7)*5
                    worktime='weekend'
                if dutydate_differ<=dutygruops_count:
                    dutydate_differ=dutydate_differ-1
                    if dutydate_differ<0:
                        dutydate_differ=dutygruops_count-1
                    dutygroups_inturn_week_ob = \
                    dutygroups.objects.filter(productname=pk,worktime=worktime,startime__lte=duty_date).order_by('startime')[dutydate_differ]
                    dutygroups_inturn_week_ob.startime = duty_date
                    serializer = dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
                    # return JsonResponse(serializer.data,status=200)
                    List.append(serializer.data)
                else:
                    dutygroups_inturn_week_ob=dutygroups.objects.filter(productname=pk,worktime=worktime,startime__lte=duty_date).\
                    order_by('startime')[((dutydate_differ-1)%dutygruops_count)]
                    dutygroups_inturn_week_ob.startime = duty_date
                    serializer = dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
                    List.append(serializer.data)
                i=i+1
                duty_date=duty_date+timedelta(days=1)
            return  JsonResponse(List,safe=False)

        loopcode = products.objects.get(id=pk).loopcode
        modifytime = products.objects.get(id=pk).modifytime
        while (modifytime < duty_date):
            if loopcode < dutygroups.objects.filter(productname_id=pk).count() - 1:
                loopcode = loopcode + 1
            else:
                loopcode = 0
            modifytime = modifytime + timedelta(days=1)
        if duty_date == datetime.now().date() and products.objects.get(id=pk).modifytime<modifytime:
            products_object=products.objects.get(id=pk)
            products_object.loopcode=loopcode
            products_object.modifytime=modifytime
            products_object.save()


        List=[]
        i=0
        while(i<duty_len):
            if dutytmp.objects.filter(startime=duty_date, productname=pk).exists():
                list_dutytmp_persons = []
                for dutytmp_ob in dutytmp.objects.filter(startime=duty_date, productname=pk):
                    dict_dutytmp_person = {"personname": dutytmp_ob.personname}
                    list_dutytmp_persons.append(dict_dutytmp_person)
                dict_dutytmp = {"productname": pk, "startime": duty_date, "persons_personname": list_dutytmp_persons}
                List.append(dict_dutytmp)
                i=i+1
                duty_date = duty_date + timedelta(days=1)
                continue
            try:
                #如果duty_date在所有值班组前面   就会抛出异常
                startime_last=dutygroups.objects.filter(startime__lte=duty_date,productname=pk).only('startime').order_by('-startime')[0].startime
            except:
                i=i+1
                duty_date = duty_date + timedelta(days=1)
                continue
            dutygroup_ob=dutygroups.objects.filter(productname=pk,startime__lte=duty_date).order_by('startime')[loopcode]
            dutygroup_ob.startime=duty_date
            if loopcode < dutygroups.objects.filter(productname_id=pk,startime__lte=duty_date).count() - 1:
                loopcode = loopcode + 1
            else:
                loopcode = 0
            i=i+1
            duty_date=duty_date+timedelta(days=1)
            serializer=dutygroupsDetailSerializers(dutygroup_ob)
            List.append(serializer.data)

        return JsonResponse(List,safe=False)


@api_view(['PUT',])
def dutyexchange(request):
    if request.method == 'PUT':
        groupid_bf=int(request.data.get('groupid_bf'))
        groupid_af=int(request.data.get('groupid_af'))
        groupid_bf_ob=dutygroups.objects.get(id=groupid_bf)
        groupid_af_ob=dutygroups.objects.get(id=groupid_af)
        if not groupid_af_ob.worktime == groupid_bf_ob.worktime :
            return JsonResponse({"msg":"exchange between groups must be the same worktime"})
        tmp=groupid_bf_ob.startime
        groupid_bf_ob.startime=groupid_af_ob.startime
        groupid_af_ob.startime=tmp
        groupid_bf_ob.save()
        groupid_af_ob.save()
        List=[]
        List.append(groupid_bf_ob)
        List.append(groupid_af_ob)
        serializer=dutygroupsSerializers(List,many=True)
        return JsonResponse(serializer.data,safe=False)

@api_view(['POST',])
def dutytmp_post(request):
    if request.method == 'POST' :
        serializer=dutytmpSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data,status=200)
        else:
            return JsonResponse(serializer.errors,status=500)


@api_view(['DELETE',])
def dutytmp_delete(request,pk):
    if request.method == 'DELETE' :
        datetmp=request.GET('datetmp')
        if datetmp is None :
            return HttpResponse(status=500)
        dutytmp.objects.filter(productname=pk,startime=datetmp).delete()
        return HttpResponse(status=204)




