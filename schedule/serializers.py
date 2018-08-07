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
    # tracks=serializers.CharField(source='productname')   #返回外键的真实值
    #productname=productsSerializers(read_only=False)   #返回外键的所有内容
    # productname=serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model=dutygroups
        fields=('id','productname','groupname','startime',)
        # depth=1     #返回一层外键的所有内容




class personsSerializers(serializers.ModelSerializer):

    class Meta:
        model=persons
        fields=('id','groupname','personname',)

class dutygroupsDetailSerializers(serializers.ModelSerializer):
    # tracks=serializers.CharField(source='productname')   #返回外键的真实值
    #productname=productsSerializers(read_only=False)   #返回外键的所有内容
    # productname=serializers.PrimaryKeyRelatedField(read_only=True)
    persons_personname=personsSerializers(many=True,read_only=True)
    class Meta:
        model=dutygroups
        fields=('id','productname','groupname','startime','persons_personname')
        # depth=1     #返回一层外键的所有内容