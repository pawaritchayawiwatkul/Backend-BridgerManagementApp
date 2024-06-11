from rest_framework import serializers
from teacher.models import Course, Teacher
    
class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    phone_number = serializers.CharField(source="user.phone_number", required=False)
    uuid = serializers.CharField(source="user.uuid", required=False)
    email = serializers.CharField(source="user.email", required=False)

    class Meta:
        model = Teacher
        fields = ("first_name", "last_name", "phone_number", "email", "uuid")

    def update(self, instance, validated_data):
        user_data = validated_data.get('user')
        if user_data:
            instance.user.first_name = user_data.get('first_name', instance.user.first_name)
            instance.user.last_name = user_data.get('last_name', instance.user.last_name)
            instance.user.phone_number = user_data.get('phone_number', instance.user.phone_number)
            instance.user.email = user_data.get('email', instance.user.email)
            instance.user.username = f'{instance.user.first_name} {instance.user.last_name}'
            instance.user.save()
            return instance
        