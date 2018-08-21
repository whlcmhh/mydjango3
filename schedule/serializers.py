from rest_framework import serializers,validators
from schedule.models import products,dutygroups,persons

class productsSerializers(serializers.ModelSerializer):
    class Meta:
        model=products
        fields=('id','productname','dutymode',)
    # def validate(self,data):
    #     if not data['dutymode']=='week' or data['dutymode'] == 'day' :
    #         raise serializers.ValidationError('dutymode must be week or day')
    #     return data
    # def validate_productname(self,value):
    #     if value in products.objects.values('productname'):
    #         raise serializers.ValidationError('productname already exits')
    #     return value
    # def validate_dutymode(self,value):
    #     if value!='week' and value !='day' :
    #         raise serializers.ValidationError('dutymode must be week or day')
    #     return value

class dutygroupsSerializers(serializers.ModelSerializer):
    # productname=serializers.CharField(source='productname.productname')   #返回外键的真实值
    #productname=productsSerializers(read_only=False)   #返回外键的所有内容
    # productname_name=serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    # productname_name=serializers.ReadOnlyField()
    class Meta:
        model=dutygroups
        fields=('id','productname','groupname','startime',)
        # depth=1     #返回一层外键的所有内容
        def validate(self,data):
            if products.objects.get(id=data['productname']).dutymode == 'week':
                DUTY_CYCLE = 7
            elif products.objects.get(id=data['productname']).dutymode == 'day':
                DUTY_CYCLE = 1
            if dutygroups.objects.all().exists():
                if (data['startime']-dutygroups.objects.all().first().startime)%DUTY_CYCLE == 0:
                    return data
                else:
                    raise serializers.ValidationError('startime不合法')
            else:
                return data



class personsSerializers(serializers.ModelSerializer):

    class Meta:
        model=persons
        fields=('id','groupname','personname',)

class dutygroupsDetailSerializers(serializers.ModelSerializer):
    persons_personname=personsSerializers(many=True,read_only=True)
    class Meta:
        model=dutygroups
        fields=('id','productname','groupname','startime','persons_personname')
