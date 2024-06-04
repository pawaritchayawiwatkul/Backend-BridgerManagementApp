from student.models import Student
from teacher.models import Teacher
# from schools.models import School
from django.db import IntegrityError
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from rest_framework.serializers import ModelSerializer, CharField
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from rest_framework.settings import api_settings
from djoser.conf import settings
from django.db import transaction
from rest_framework.utils import html, model_meta, representation
import copy
from rest_framework.fields import SkipField
from rest_framework.relations import Hyperlink, PKOnlyObject  # NOQA # isort:skip

User = get_user_model()
    
ALL_FIELDS = '__all__'

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['password', 'email', 'first_name', 'last_name', 'is_teacher', 'birth_date', 'phone_number']
    
    def to_native(self, obj):
        """
        Serialize objects -> primitives.
        """
        ret = self._dict_class()
        ret.fields = {}

        for field_name, field in self.fields.items():
            # --- BEGIN EDIT --- #
            if field_name in self.opts.non_native_fields:
                continue
            # --- END --- #
            field.initialize(parent=self, field_name=field_name)
            key = self.get_field_key(field_name)
            value = field.field_to_native(obj, field_name)
            ret[key] = value
            ret.fields[key] = field
        return ret
    
    def create(self, validated_data):
        try:
            validated_data["username"] = f'{validated_data["first_name"]} {validated_data["last_name"]}'
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")
        if user.is_teacher:
            Teacher.objects.create(
                user=user,
            )
        else:
            Student.objects.create(
                user=user, 
            )
        return user

    def validate(self, attrs):
        password = attrs.get("password")
        try:
            validate_password(password)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )
        return attrs

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = {}
        fields = self._readable_fields
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['email', 'full_name']
