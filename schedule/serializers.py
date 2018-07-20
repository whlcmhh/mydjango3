from rest_framework import serializers,validators
from schedule.models import products,dutygroups,persons

class productsSerializers(serializers.ModelSerializer):
    class Meta:
        model=products
        fields=('id','productname','dutymode',)
    # def validate(self,attrs):

class dutygroupsSerializers(serializers.ModelSerializer):
    class Meta:
        model=dutygroups

        fields=('id','productname','groupname','startime',)



class personsSerializers(serializers.ModelSerializer):
    class Meta:
        model=persons
        fields=('id','productname','groupname','personname',)
