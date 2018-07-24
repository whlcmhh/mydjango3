from rest_framework import serializers,validators
from schedule.models import products,dutygroups,persons

class productsSerializers(serializers.ModelSerializer):
    class Meta:
        model=products
        fields=('id','productname','dutymode',)
    # def validate(self,attrs):

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
        fields=('id','productname','groupname','personname',)
