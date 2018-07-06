from rest_framework import serializers
from schedule.models import sch

class schSerializer(serializers.Serializer):
    id=serializers.IntegerField(read_only=True)
    name=serializers.CharField(max_length=20)
    date=serializers.DateField()

    def create(self,validated_data):
        return sch.objects.create(**validated_data)
    def update(self,instance,validated_data):
        instance.id=validated_data.get('id',instance.id)
        instance.name=validated_data.get('name',instance.name)
        instance.date=validated_data.get('date',instance.date)
        instance.save()
        return instance
