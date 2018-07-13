from django.db import models


# Create your models here.

class sch(models.Model):
    id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=30)
    date=models.DateField()
    # class Meta:
    #     ordring=('id',)
    def __str__(self):
        return self.name

class product(models.Model):
    MODE_CHOICES=(('week','周'),('day','日'))
    productname=models.CharField(max_length=30)
    dutymode=models.CharField(max_length=30,choices=MODE_CHOICES,default='week')


class dutygroup(models.Model):
    productname=models.ForeignKey('product',to_field='productname',on_delete=models.CASCADE)
    groupname=models.CharField(max_length=30)
    startime = models.DateField()
    class Meta:
        unique_together=('productname','groupname')

class person(models.Model):
    productname=models.ForeignKey('dutygroup',to_field=productname,on_delete=models.CASCADE)
    groupname=models.ForeignKey('dutygroup',to_field=groupname,on_delete=models.CASCADE)
    personname=models.CharField(max_length=30)

