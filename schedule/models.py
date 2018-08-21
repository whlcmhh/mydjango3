from django.db import models



# Create your models here.


class products(models.Model):
    MODE_CHOICES=(('week','周'),('day','日'),)
    productname=models.CharField(max_length=30,unique=True)
    dutymode=models.CharField(max_length=30,choices=MODE_CHOICES,default='week')


class dutygroups(models.Model):
    productname=models.ForeignKey('products',on_delete=models.CASCADE)
    groupname=models.CharField(max_length=30)
    startime = models.DateField()
    class Meta:
        unique_together=('productname','groupname')
    # @property
    # def productname_name(self):
    #     return self.productname.productname






class persons(models.Model):
    groupname=models.ForeignKey('dutygroups',related_name='persons_personname',on_delete=models.CASCADE)
    personname=models.CharField(max_length=30)
