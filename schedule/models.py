from django.db import models
from rest_framework import serializers


# Create your models here.


class products(models.Model):
    MODE_CHOICES=(('week','周'),('day','日'))
    productname=models.CharField(max_length=30)
    dutymode=models.CharField(max_length=30,choices=MODE_CHOICES,default='week')

class productsSerializers(serializers.ModelSerializer):
    class Meta:
        model=products
        fields='__all__'
    # def validate(self,attrs):


class dutygroups(models.Model):
    productname=models.ForeignKey('products',on_delete=models.CASCADE)
    groupname=models.CharField(max_length=30)
    startime = models.DateField()
    class Meta:
        unique_together=('productname','groupname')

class dutygroupsSerializers(serializers.ModelSerializer):
    class Meta:
        model=dutygroups
        fields='__all__'

class persons(models.Model):
    productname=models.ForeignKey('dutygroups',related_name='persons_productname',on_delete=models.CASCADE)
    groupname=models.ForeignKey('dutygroups',related_name='persons_groupname',on_delete=models.CASCADE)
    personname=models.CharField(max_length=30)

class personsSerializers(serializers.ModelSerializer):
    class Meta:
        model=persons
        fields='__all__'
