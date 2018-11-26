from django.db import models



# Create your models here.


class products(models.Model):
    MODE_CHOICES=(('week','周'),('day','日'),('ops','运维'))
    productname=models.CharField(max_length=30,unique=True)
    dutymode=models.CharField(max_length=30,choices=MODE_CHOICES,default='week')
    loopcode=models.IntegerField(default=0)
    modifytime=models.DateField(null=True,blank=True,default='2018-01-01')


class dutygroups(models.Model):
    MODE_CHOICES = (('weekend', '周末'), ('weekday', '工作日'),)
    productname=models.ForeignKey('products',on_delete=models.CASCADE)
    groupname=models.CharField(max_length=30)
    startime = models.DateField()
    worktime=models.CharField(max_length=30,choices=MODE_CHOICES,blank=True,null=True)

    class Meta:
        unique_together=('productname','groupname')
    # @property
    # def productname_name(self):
    #     return self.productname.productname

class dutytmp(models.Model):
    personname=models.ForeignKey('persondetail',related_name='persondetail_tmp',to_field='personname',on_delete=models.CASCADE)
    startime=models.DateField()
    productname=models.ForeignKey('products',on_delete=models.CASCADE)

class persondetail(models.Model):
    personname=models.CharField(max_length=30,unique=True)
    productname=models.ForeignKey('products',on_delete=models.CASCADE)
    mobilephone=models.CharField(max_length=11,blank=True)
    email=models.EmailField(blank=True)
    QQ=models.CharField(max_length=30,blank=True)

class persons(models.Model):
    groupname=models.ForeignKey('dutygroups',related_name='persons_personname',on_delete=models.CASCADE)
    personname=models.ForeignKey('persondetail',related_name='persondetail_set',to_field='personname',on_delete=models.CASCADE)