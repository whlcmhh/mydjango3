from django.db import models



# Create your models here.


class products(models.Model):
    MODE_CHOICES=(('week','周'),('day','日'))
    productname=models.CharField(max_length=30)
    dutymode=models.CharField(max_length=30,choices=MODE_CHOICES,default='week')
    def __str__(self):
        return  self.productname

class dutygroups(models.Model):
    productname=models.ForeignKey('products',on_delete=models.CASCADE)
    groupname=models.CharField(max_length=30)
    startime = models.DateField()
    class Meta:
        unique_together=('productname','groupname')
    def __str__(self):
        return self.groupname


class persons(models.Model):
    productname=models.ForeignKey('dutygroups',related_name='persons_productname',on_delete=models.CASCADE)
    groupname=models.ForeignKey('dutygroups',related_name='persons_groupname',on_delete=models.CASCADE)
    personname=models.CharField(max_length=30)
    def __str__(self):
        return self.personname
