from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.core import serializers
from schedule.serializers import products,productsSerializers,dutygroups,dutygroupsSerializers,persons,personsSerializers,dutygroupsDetailSerializers
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
        data['startime']=datetime.strptime(data['startime'],'%Y-%m-%d').date()
        if dutygroups.objects.filter(productname=data['productname'],groupname=data['groupname']).exists():
            return JsonResponse({'msg':'groupname must be unique'})
        if products.objects.get(id=data['productname']).dutymode == 'week' :
            DUTY_CYCLE=7
        elif products.objects.get(id=data['productname']).dutymode == 'day':
            DUTY_CYCLE=1
        if dutygroups.objects.filter(productname=data['productname']).exists():
            if not (data['startime'] - dutygroups.objects.filter(productname=data['productname']).first().startime).days % DUTY_CYCLE == 0:
                return JsonResponse({'msg':'date is not legal'})

        #先查看产品线内是否已有值班组
        if not dutygroups.objects.filter(productname=data['productname']).exists():
            serializer=dutygroupsSerializers(data=data)
        #新纪录的startime在所有的startime之前
        elif data['startime']<dutygroups.objects.filter(productname=data['productname']).order_by('startime').first().startime:
            startime_new=dutygroups.objects.filter(productname=data['productname']).order_by('startime').first().startime
            tmp = startime_new
            cycle_num_sum=0
            for i in dutygroups.objects.filter(productname=data['productname'], startime__gt=startime_new).order_by(
                    'startime').all():
                diff_btw = (i.startime - tmp).days - DUTY_CYCLE
                print(diff_btw, 'diff_btw')
                dutygroups_count = dutygroups.objects.filter(productname=data['productname'], startime__lte=tmp+timedelta(cycle_num_sum*DUTY_CYCLE)).count()
                cycle_num = diff_btw // (dutygroups_count * DUTY_CYCLE)
                tmp2 = i.startime
                dutygroups.objects.filter(productname=data['productname'], startime__gt=tmp+timedelta(cycle_num_sum*DUTY_CYCLE)).update(
                    startime=F('startime') + timedelta(cycle_num * DUTY_CYCLE))
                cycle_num_sum=cycle_num_sum+cycle_num
                tmp = tmp2
            serializer=dutygroupsSerializers(data=data)
        #在中间
        elif data['startime']<=dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime:

            startime_last = dutygroups.objects.filter(startime__lt=data['startime'],
                                                      productname=data['productname']).order_by(
                '-startime').first().startime
            diff_before = (data['startime'] - startime_last).days

            startime_new = dutygroups.objects.filter(startime__gte=data['startime'],
                                                     productname=data['productname']).order_by(
                'startime').first().startime

            dutygroups_count = dutygroups.objects.filter(startime__lt=data['startime'],
                                                         productname=data['productname']).count()

            week_inturn = (diff_before - DUTY_CYCLE) // (
                        dutygroups.objects.filter(startime__lt=data['startime'],
                                                  productname=data['productname']).count() * DUTY_CYCLE)
            day_inturn = (diff_before - DUTY_CYCLE) % (dutygroups.objects.filter(startime__lt=data['startime'],
                                                                                 productname=data[
                                                                                     'productname']).count() * DUTY_CYCLE)
            if not (data['startime'] - dutygroups.objects.filter(startime__lt=data['startime'],
                                                                 productname=data['productname']).order_by(
                    '-startime').first().startime).days % (
                           dutygroups.objects.filter(startime__lt=data['startime'], productname=data[
                               'productname']).count() * DUTY_CYCLE) == DUTY_CYCLE:
                week_inturn = week_inturn + 1

            data_startime_new = startime_last + timedelta(
                DUTY_CYCLE + (week_inturn) * DUTY_CYCLE * dutygroups_count)
            data['startime'] = data_startime_new
            print(data['startime'],'data_startime')
            diff_after = (startime_new - data['startime']).days
            week_inturn_after = (diff_after // (dutygroups_count*DUTY_CYCLE))+1
            print(diff_after,'diff_after')
            if diff_after <=0 :
                week_inturn_after=1
            tmp=startime_new
            cycle_num_sum = 0
            for i in dutygroups.objects.filter(productname=data['productname'], startime__gt=startime_new).order_by('startime').all():
                diff_btw=(i.startime-tmp).days-DUTY_CYCLE
                print(diff_btw,'diff_btw')
                dutygroups_count = dutygroups.objects.filter(productname=data['productname'],startime__lte=tmp+timedelta(cycle_num_sum*DUTY_CYCLE)).count()
                cycle_num=diff_btw//(dutygroups_count*DUTY_CYCLE)
                tmp2=i.startime
                dutygroups.objects.filter(productname=data['productname'],startime__gt=tmp+timedelta(cycle_num_sum*DUTY_CYCLE)).update(startime=F('startime')+timedelta(cycle_num*DUTY_CYCLE))
                cycle_num_sum=cycle_num_sum+cycle_num
                tmp=tmp2

            dutygroups.objects.filter(startime__gte=startime_new,productname=data['productname']).update(
                startime=F('startime') + timedelta((week_inturn_after) * DUTY_CYCLE))



            serializer = dutygroupsSerializers(data=data)

        #在最后
        elif data['startime']>dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime:
            if (data['startime']-dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime).days == DUTY_CYCLE:
                serializer=dutygroupsSerializers(data=data)
            else:
                startime_last = dutygroups.objects.filter(productname=data['productname']).order_by(
                    '-startime').first().startime
                diff_before = (data['startime'] - startime_last).days
                dutygroups_count = dutygroups.objects.filter(productname=data['productname']).count()
                week_inturn = (diff_before - DUTY_CYCLE) // (
                        dutygroups.objects.filter(
                            productname=data['productname']).count() * DUTY_CYCLE)
                if not (data['startime'] - dutygroups.objects.filter(
                        productname=data['productname']).order_by(
                    '-startime').first().startime).days % (
                               dutygroups.objects.filter(startime__lt=data['startime'], productname=data[
                                   'productname']).count() * DUTY_CYCLE) == DUTY_CYCLE:
                    week_inturn = week_inturn + 1
                data_startime_new = startime_last + timedelta(
                    DUTY_CYCLE + (week_inturn) * DUTY_CYCLE * dutygroups_count)
                data['startime'] = data_startime_new
                # data['startime']=dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime+timedelta(DUTY_CYCLE+dutygroups.objects.filter(productname=data['productname']).count()*DUTY_CYCLE)
                serializer = dutygroupsSerializers(data=data)



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
        # put_delete_count = dutygroups.objects.filter(productname=data['productname'],
        #                                              startime__lte=startime_old).count()
        data['startime']=datetime.strptime(data['startime'],'%Y-%m-%d').date()
        if dutygroups.objects.filter(groupname=data['groupname']).exclude(pk=pk).exists():
            return JsonResponse({'msg':'groupname must be unique'})
        if products.objects.get(id=pid).dutymode == 'week':
            DUTY_CYCLE = 7
        elif products.objects.get(id=pid).dutymode == 'day':
            DUTY_CYCLE = 1
        if not (data['startime'] - dutygroups.objects.filter(productname=data['productname']).first().startime).days % DUTY_CYCLE == 0:
            return JsonResponse({'msg':'date is not legal'})
        #查看修改的日期和已有日期是否重合
        group_already=dutygroups.objects.filter(productname=data['productname'], startime=data['startime'])
        if group_already.exists():
            group_already_ob=dutygroups.objects.get(productname=data['productname'], startime=data['startime'])
            dutygroup.startime,group_already_ob.startime = group_already_ob.startime,dutygroup.startime
            dutygroup.groupname=data['groupname']
            dutygroup.save()
            group_already_ob.save()
            serializer=dutygroupsSerializers(dutygroup)
            return JsonResponse(serializer.data)
        else:
            #先查看产品线内是否已有值班组
            if not dutygroups.objects.filter(productname=data['productname']).exists():
                serializer=dutygroupsSerializers(data=data)
            #新纪录的startime在所有的startime之前
            elif data['startime']<dutygroups.objects.filter(productname=data['productname']).order_by('startime').first().startime:
                startime_new = dutygroups.objects.filter(productname=data['productname']).order_by(
                    'startime').first().startime
                tmp = startime_new
                cycle_num_sum = 0
                for i in dutygroups.objects.filter(productname=data['productname'], startime__gt=startime_new).order_by(
                        'startime').all():
                    diff_btw = (i.startime - tmp).days - DUTY_CYCLE
                    print(diff_btw, 'diff_btw')
                    dutygroups_count = dutygroups.objects.filter(productname=data['productname'],
                                                                 startime__lte=tmp + timedelta(
                                                                     cycle_num_sum * DUTY_CYCLE)).count()
                    cycle_num = diff_btw // (dutygroups_count * DUTY_CYCLE)
                    tmp2 = i.startime
                    dutygroups.objects.filter(productname=data['productname'],
                                              startime__gt=tmp + timedelta(cycle_num_sum * DUTY_CYCLE)).update(
                        startime=F('startime') + timedelta(cycle_num * DUTY_CYCLE))
                    cycle_num_sum = cycle_num_sum + cycle_num
                    tmp = tmp2
                serializer=dutygroupsSerializers(data=data)
            #在中间
            elif data['startime']<=dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime:
                #和已有的startime重合
                if  dutygroups.objects.filter(productname=data['productname'],startime=data['startime']).exists():
                    dutygroups.objects.filter(productname=data['productname'],startime__gte=data['startime']).update(startime=F('startime')+timedelta(DUTY_CYCLE))
                    serializer=dutygroupsSerializers(data=data)

                #不重合
                else:
                    startime_last = dutygroups.objects.filter(startime__lt=data['startime'],
                                                              productname=data['productname']).order_by(
                        '-startime').first().startime
                    diff_before = (data['startime'] - startime_last).days

                    startime_new = dutygroups.objects.filter(startime__gte=data['startime'],
                                                             productname=data['productname']).order_by(
                        'startime').first().startime
                    print(startime_new,'startime_new')
                    dutygroups_count = dutygroups.objects.filter(startime__lt=data['startime'],
                                                                 productname=data['productname']).count()

                    week_inturn = (diff_before - DUTY_CYCLE) // (
                            dutygroups.objects.filter(startime__lt=data['startime'],
                                                      productname=data['productname']).count() * DUTY_CYCLE)
                    day_inturn = (diff_before - DUTY_CYCLE) % (dutygroups.objects.filter(startime__lt=data['startime'],
                                                                                         productname=data[
                                                                                             'productname']).count() * DUTY_CYCLE)
                    if not (data['startime'] - dutygroups.objects.filter(startime__lt=data['startime'],
                                                                         productname=data['productname']).order_by(
                        '-startime').first().startime).days % (
                                   dutygroups.objects.filter(startime__lt=data['startime'], productname=data[
                                       'productname']).count() * DUTY_CYCLE) == DUTY_CYCLE:
                        week_inturn = week_inturn + 1

                    data_startime_new = startime_last + timedelta(
                        DUTY_CYCLE + (week_inturn) * DUTY_CYCLE * dutygroups_count)
                    data['startime'] = data_startime_new
                    print(data['startime'],'data..startime')
                    #对data['startime']进行判断，如果已存在就不进行下面的
                    diff_after = (startime_new - data['startime']).days
                    print(startime_new,'startime_new')
                    print(diff_after,'diff_after')

                    week_inturn_after = (diff_after // (dutygroups_count*DUTY_CYCLE))+1
                    if diff_after <=0:
                        week_inturn_after = 1

                    print(week_inturn_after,'week_inturn_after')
                    tmp = startime_new
                    cycle_num_sum=0
                    for i in dutygroups.objects.filter(productname=data['productname'],
                                                       startime__gt=startime_new).order_by('startime').all():
                        diff_btw = (i.startime - tmp).days - DUTY_CYCLE
                        print(diff_btw,'diff_btw')
                        dutygroups_count = dutygroups.objects.filter(productname=data['productname'],
                                                                     startime__lte=tmp+timedelta(cycle_num_sum*DUTY_CYCLE)).count()
                        cycle_num = diff_btw // (dutygroups_count * DUTY_CYCLE)
                        tmp2 = i.startime
                        dutygroups.objects.filter(productname=data['productname'], startime__gt=tmp+timedelta(cycle_num_sum*DUTY_CYCLE)).update(
                            startime=F('startime') + timedelta(cycle_num * DUTY_CYCLE))
                        cycle_num_sum = cycle_num_sum + cycle_num
                        tmp = tmp2

                    dutygroups.objects.filter(startime__gte=startime_new, productname=data['productname']).update(
                        startime=F('startime') + timedelta((week_inturn_after) * DUTY_CYCLE))
                    startime_old_alter = dutygroups.objects.get(pk=pk).startime

                    print(startime_old_alter,'startime_old_alter')


                    serializer = dutygroupsSerializers(data=data)

            #在最后
            elif data['startime']>dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime:
                if (data['startime']-dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime).days == DUTY_CYCLE:
                    serializer=dutygroupsSerializers(data=data)

                else:
                    startime_last = dutygroups.objects.filter(productname=data['productname']).order_by(
                        '-startime').first().startime
                    diff_before = (data['startime'] - startime_last).days
                    dutygroups_count = dutygroups.objects.filter(productname=data['productname']).count()
                    week_inturn = (diff_before - DUTY_CYCLE) // (
                                dutygroups.objects.filter(
                                                          productname=data['productname']).count() * DUTY_CYCLE)
                    if not (data['startime'] - dutygroups.objects.filter(
                                                                         productname=data['productname']).order_by(
                            '-startime').first().startime).days % (
                                   dutygroups.objects.filter(startime__lt=data['startime'], productname=data[
                                       'productname']).count() * DUTY_CYCLE) == DUTY_CYCLE:
                        week_inturn = week_inturn + 1
                    data_startime_new = startime_last + timedelta(
                        DUTY_CYCLE + (week_inturn) * DUTY_CYCLE * dutygroups_count)
                    data['startime'] = data_startime_new
                    # data['startime']=dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime+timedelta(DUTY_CYCLE+dutygroups.objects.filter(productname=data['productname']).count()*DUTY_CYCLE)
                    serializer=dutygroupsSerializers(data=data)

            # print(startime_old )
            # print(dutygroups.objects.filter(productname=data['productname']).order_by('startime').first().startime)
            # print(dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime)

            # if startime_old > dutygroups.objects.filter(productname=data['productname']).order_by('startime').first().startime and startime_old < dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime:
            #     print(1)


            serializer=dutygroupsSerializers(dutygroup,data=data)
        if serializer.is_valid():
            serializer.save()
            if startime_old < dutygroups.objects.filter(productname=data['productname']).order_by('-startime').first().startime:

                if not startime_old_alter == 0:
                    startime_old=startime_old_alter

                diff = (dutygroups.objects.filter(productname=data['productname'], startime__gt=startime_old).order_by(
                    'startime').first().startime - startime_old).days
                # dutygroups_count = put_delete_count

                dutygroups_count = dutygroups.objects.filter(productname=data['productname'],
                                                             startime__lte=startime_old).count()


                week_num_after=(diff-DUTY_CYCLE)//(DUTY_CYCLE*dutygroups_count)
                #
                startime_new=dutygroups.objects.filter(productname=data['productname'], startime__gt=startime_old).order_by(
                    'startime').first().startime
                print(startime_old,'startime_old')
                print(startime_new,'startime_new')
                tmp = startime_new
                cycle_num_sum=0
                for i in dutygroups.objects.filter(productname=data['productname'],
                                                   startime__gt=startime_new).order_by('startime').all():
                    print(i.startime,'i.startime')
                    print(tmp,'tmp')
                    diff_btw = (i.startime - tmp).days - DUTY_CYCLE
                    print(diff_btw,'diff_btw2')
                    dutygroups_count = dutygroups.objects.filter(productname=data['productname'],
                                                                 startime__lte=tmp-timedelta(cycle_num_sum*DUTY_CYCLE)).count()
                    cycle_num = diff_btw // (dutygroups_count * DUTY_CYCLE)
                    print('yushu',diff_btw % (dutygroups_count * DUTY_CYCLE))
                    tmp2 = i.startime
                    dutygroups.objects.filter(productname=data['productname'], startime__gt=tmp-timedelta(cycle_num_sum*DUTY_CYCLE)).update(
                        startime=F('startime') - timedelta(cycle_num * DUTY_CYCLE))
                    cycle_num_sum = cycle_num_sum + cycle_num
                    tmp = tmp2
                print(week_num_after,'week_num_after')
                dutygroups.objects.filter(productname=data['productname'], startime__gt=startime_old).update(
                    startime=F('startime') - timedelta((week_num_after+1)*DUTY_CYCLE))
            serializer=dutygroupsSerializers(dutygroups.objects.get(pk=pk))

            return JsonResponse(serializer.data,status=201)
        else:
            return JsonResponse(serializer.errors)
    if request.method == 'DELETE':
        dutygroup.delete()

        if products.objects.get(id=pid).dutymode == 'week':
            DUTY_CYCLE = 7
        elif products.objects.get(id=pid).dutymode == 'day':
            DUTY_CYCLE = 1

        if dutygroup.startime > dutygroups.objects.filter(productname=pid).order_by('startime').first().startime and dutygroup.startime < dutygroups.objects.filter(productname=pid).order_by('-startime').first().startime:
            #要删除的节点和下一个节点的差
            diff=(dutygroups.objects.filter(productname=pid,startime__gt=dutygroup.startime).order_by('startime').first().startime-dutygroup.startime).days
            #前面生效的值班组数量（包含生效值班组自身）
            dutygroups_count = dutygroups.objects.filter(productname=pid,
                                                         startime__lt=dutygroup.startime).count()+1
            week_num_after = (diff - DUTY_CYCLE) // (DUTY_CYCLE * dutygroups_count)
            startime_new = dutygroups.objects.filter(productname=pid,startime__gt=dutygroup.startime).order_by('startime').first().startime
            tmp=startime_new
            cycle_num_sum=0
            for i in dutygroups.objects.filter(productname=pid,
                                               startime__gt=startime_new).order_by('startime').all():
                diff_btw = (i.startime - tmp).days - DUTY_CYCLE
                dutygroups_count = dutygroups.objects.filter(productname=pid,
                                                             startime__lte=tmp-timedelta(cycle_num_sum*DUTY_CYCLE)).count()
                cycle_num = diff_btw // (dutygroups_count * DUTY_CYCLE)
                tmp2 = i.startime
                dutygroups.objects.filter(productname=pid, startime__gt=tmp-timedelta(cycle_num_sum*DUTY_CYCLE)).update(
                    startime=F('startime') - timedelta(cycle_num * DUTY_CYCLE))
                cycle_num_sum = cycle_num_sum + cycle_num
                tmp = tmp2
            dutygroups.objects.filter(productname=pid,startime__gt=dutygroup.startime).update(startime=F('startime')-timedelta((week_num_after+1)*DUTY_CYCLE))
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

@api_view(['GET',])
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
        #值班表时间长度,默认30天
        duty_len=request.GET.get('len')
        if duty_len is None:
            duty_len=30
        else:
            duty_len=int(duty_len)
        # 查看当前生效的值班组
        if duty_date + timedelta(days=duty_len) < dutygroups.objects.filter(productname=pk).only('startime').order_by('startime')[0].startime:
            return JsonResponse({"msg": "dutylist is null"})
        # 查看按周还是按日
        if products.objects.get(id=pk).dutymode == 'week' :
            DUTY_CYCLE=7
        elif products.objects.get(id=pk).dutymode == 'day':
            DUTY_CYCLE=1

        List=[]
        i=0
        while(i<duty_len):

            #最近的一个值班组的开始时间
            startime_last=dutygroups.objects.filter(startime__lt=duty_date,productname=pk).only('startime').order_by('-startime')[0].startime
            #当前时间和和最近一个值班组的开始时间时间差
            startime_differ=(duty_date-startime_last).days
            #时间差小于7天，直接返回最近的值班组
            if startime_differ<=DUTY_CYCLE :
                dutygroups_inturn_week_ob=dutygroups.objects.filter(productname=pk).order_by('-startime')[0]
                dutygroups_inturn_week_ob.startime = duty_date
                serializer=dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
                # return JsonResponse(serializer.data,status=200)
                List.append(serializer.data)
            #时间差大于7天
            else:
                dutygruops_count=dutygroups.objects.filter(startime__lt=duty_date,productname=pk).count()
                startime_differ=startime_differ+DUTY_CYCLE
                #轮到哪一周
                dutygroups_inturn_week=(startime_differ%(dutygruops_count*DUTY_CYCLE))//DUTY_CYCLE
                #轮到哪一天
                dutygroups_inturn_day=(startime_differ%(dutygruops_count*DUTY_CYCLE))%DUTY_CYCLE
                dutygroups_inturn_week_ob=dutygroups.objects.filter(startime__lt=duty_date,productname=pk).order_by('startime')[dutygroups_inturn_week]
                dutygroups_inturn_week_ob.startime=duty_date
                serializer=dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
                # return JsonResponse(serializer.data,status=200)
                List.append(serializer.data)
            i=i+1
            duty_date=duty_date+timedelta(days=1)

        return JsonResponse(List,safe=False)

@api_view(['GET',])
def dutyday(request,pk):
    if request.method == 'GET':
        #查找对应产品线
        if not dutygroups.objects.filter(productname=pk).exists():
            return JsonResponse({"msg":"dutygroup is null"})
        #取得值班日期
        duty_date = request.GET.get('date')
        if duty_date is None:
            duty_date = datetime.now().date()
        else:
            duty_date = datetime.strptime(duty_date, '%Y-%m-%d').date()
        # 查看当前生效的值班组
        if duty_date < dutygroups.objects.filter(productname=pk).only('startime').order_by('startime')[0].startime:
            return JsonResponse({"msg": "dutylist is null"})
        # 查看按周还是按日
        if products.objects.get(id=pk).dutymode == 'week':
            DUTY_CYCLE = 7
        elif products.objects.get(id=pk).dutymode == 'day':
            DUTY_CYCLE = 1
        # 最近的一个值班组的开始时间
        startime_last = dutygroups.objects.filter(startime__lt=duty_date, productname=pk).only('startime').order_by('-startime')[0].startime
        # 当前时间和和最近一个值班组的开始时间时间差
        startime_differ = (duty_date - startime_last).days
        if startime_differ < DUTY_CYCLE :
            dutygroups_inturn_week_ob = dutygroups.objects.filter(productname=pk).order_by('-startime')[0]
            dutygroups_inturn_week_ob.startime = duty_date
            serializer = dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
        else:
            dutygruops_count = dutygroups.objects.filter(startime__lt=duty_date, productname=pk).count()
            startime_differ = startime_differ + DUTY_CYCLE
            # 轮到哪一周
            dutygroups_inturn_week = (startime_differ % (dutygruops_count * DUTY_CYCLE)) // DUTY_CYCLE
            dutygroups_inturn_week_ob = dutygroups.objects.filter(startime__lt=duty_date, productname=pk).order_by('startime')[dutygroups_inturn_week]
            dutygroups_inturn_week_ob.startime = duty_date
            serializer = dutygroupsDetailSerializers(dutygroups_inturn_week_ob)
        return JsonResponse(serializer.data,safe=False)

@api_view(['PUT',])
def dutyexchange(request):
    if request.method == 'PUT':
        groupid_bf=int(request.data.get('groupid_bf'))
        groupid_af=int(request.data.get('groupid_af'))
        groupid_bf_ob=dutygroups.objects.get(id=groupid_bf)
        groupid_af_ob=dutygroups.objects.get(id=groupid_af)
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





