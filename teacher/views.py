from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ViewSet
# from teacher.models import Course
from rest_framework.response import Response
from teacher.models import Teacher
from teacher.serializers import ProfileSerializer
from student.models import Student

@permission_classes([IsAuthenticated])
class ProfileViewSet(ViewSet):
    def retrieve(self, request):
        user = request.user
        student = Teacher.objects.select_related("user").get(user_id=user.id)
        ser = ProfileSerializer(instance=student)
        return Response(ser.data)
    
    def update(self, request):
        user = request.user
        student = Teacher.objects.select_related("user").get(user_id=user.id)
        ser = ProfileSerializer(data=request.data)
        if ser.is_valid():
            print(ser.validated_data)
            student = ser.update(student, ser.validated_data)
            return Response(status=200)
        else:
            return Response(ser.errors, status=400)
        
    def add(self, request, student_uuid):
        try:
            student = Student.objects.get(user__uuid=student_uuid)
        except:
            return Response({"error_messages": ["Invalid UUID"]}, status=400)
        user = request.user
        teacher = get_object_or_404(Teacher, user_id=user.id)
        if not teacher.teacher.filter(id=student.id).exists():
            teacher.teacher.add(student)
            teacher.school.add(student.school_id)
        return Response(status=200)