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

