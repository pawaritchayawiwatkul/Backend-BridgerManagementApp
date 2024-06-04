from rest_framework.views import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import api_view
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from student.models import CourseRegistration, Student, Course, Lesson, StudentTeacherRelation
from teacher.models import UnavailableTimeOneTime, UnavailableTimeRegular, Teacher
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, F
from datetime import datetime
from django.db.models.functions import ExtractWeek, Extract, ExtractMonth
from django.core.exceptions import ValidationError
from student.serializers import ListLessonSerializer, CourseRegistrationSerializer, LessonSerializer, ListTeacherSerializer, ListCourseRegistrationSerializer, ListLessonDateTimeSerializer, ProfileSerializer
from django.shortcuts import get_object_or_404
from dateutil.relativedelta import relativedelta

@permission_classes([IsAuthenticated])
class ProfileViewSet(ViewSet):
    def retrieve(self, request):
        user = request.user
        student = Student.objects.select_related("user").get(user_id=user.id)
        ser = ProfileSerializer(instance=student)
        return Response(ser.data)
    
    def update(self, request):
        user = request.user
        student = Student.objects.select_related("user").get(user_id=user.id)
        ser = ProfileSerializer(data=request.data)
        if ser.is_valid():
            print(ser.validated_data)
            student = ser.update(student, ser.validated_data)
            return Response(status=200)
        else:
            return Response(ser.errors, status=400)

@permission_classes([IsAuthenticated])
class TeacherViewset(ViewSet):
    def list(self, request):
        user = request.user
        teacher = StudentTeacherRelation.objects.select_related("teacher__school", "teacher__user").filter(student__user_id=user.id)
        ser = ListTeacherSerializer(instance=teacher, many=True)
        return Response(ser.data)
    
@permission_classes([IsAuthenticated])
class CourseViewset(ViewSet):
    def list(self, request):
        teacher_uuid = request.data.get("teacher_uuid")
        filters = {
            'student__user_id': request.user.id,
        }
        if request.data.get("all_course"):
            filters['completed'] = True
        else:
            filters['completed'] = False

        if teacher_uuid:
            # Assuming you have a Teacher model with a UUID field
            teacher = get_object_or_404(Teacher, user__uuid=teacher_uuid)
            filters['teacher'] = teacher

        courses = CourseRegistration.objects.select_related("course").filter(**filters)
        ser = ListCourseRegistrationSerializer(instance=courses, many=True)
        return Response(ser.data)

    def get_available_time(self, request, code):
        date_str = request.data.get("date")
        if not date_str:
            return Response({"error_messages": ["Please Provide Date"]}, status=400)
        date = datetime.strptime(date_str, "%Y-%m-%d")
        day_number = date.weekday() + 1
        regis = CourseRegistration.objects.select_related('teacher', 'course').get(uuid=code)
        booked_lessons = Lesson.objects.filter(
            registration=regis,
            booked_datetime__date=date
        ).values_list("booked_datetime", flat=True)
        unavailable_regular = UnavailableTimeRegular.objects.filter(
            teacher=regis.teacher,
            day=str(day_number)
        ).annotate(
        ).values_list("time", "duration")
        unavailable_times = UnavailableTimeOneTime.objects.filter(
            teacher=regis.teacher, 
            datetime__date=date
        ).values_list("datetime", "duration")
        return Response(data={
            'available'
            "lessons": {
                "booked": list(booked_lessons),
                "duration": regis.course.duration
            },
            "unavailable": list(unavailable_regular) + list(unavailable_times)
        })
    
    def retrieve(self, request, code):
        filters = {
            "registration__uuid": code,
            "registration__student__user_id": request.user.id
        }
        lessons = Lesson.objects.filter(**filters)
        ser = ListLessonDateTimeSerializer(instance=lessons, many=True)
        return Response(ser.data, status=200)
    
    def create(self, request):
        data = dict(request.data)
        data["student_id"] = request.user.id
        ser = CourseRegistrationSerializer(data=data)
        if ser.is_valid():
            obj = ser.create(validated_data=ser.validated_data)
            return Response({"registration_id": obj.uuid}, status=200)
        else:
            return Response(ser.errors, status=400)

@permission_classes([IsAuthenticated])
class LessonViewset(ViewSet):
    def week(self, request):
        start_of_week = request.data.get("start")
        end_of_week = request.data.get("end")
        if start_of_week and end_of_week:
            try:
                lessons = Lesson.objects.filter(
                    registration__student__user_id=request.user.id,
                    booked_datetime__date__range=[start_of_week, end_of_week]
                    )
            except ValidationError as e:
                return Response({"error_message": e}, status=400)
            ser = ListLessonSerializer(instance=lessons, many=True)
            return Response(ser.data, status=200)
        else:
            return Response({"error_message": ["Start or end is empty", ]}, status=400)

    def progress(self, request, progress_type):
        today_date = request.data.get("date_of_today")
        today_date = datetime.strptime(today_date, "%Y-%m-%d")
        if not today_date:
            return Response({"error_message": ["Please enter today's date", ]}, status=400)
        if progress_type == "daily":
            seven_days_ago = today_date - timedelta(days=7)
            stop_day = today_date + timedelta(days=1)
            completed_lessons = Lesson.objects.filter(
                attended=True,  # Assuming 'attended' field indicates completion
                booked_datetime__gte=seven_days_ago,
                booked_datetime__lt=stop_day,
                registration__student__user_id=request.user.id
            ).order_by('booked_datetime').annotate(
                day_number=Extract(F('booked_datetime'), 'doy')  # Extract the week number from the attended_date
            ).values('day_number').annotate(completed_lessons_count=Count('id'))
            return Response(list(completed_lessons))
        elif progress_type == "weekly":
            start_of_week = today_date - timedelta(days=today_date.weekday())  # Assuming Monday is the start of the week
            start_date = today_date - timedelta(weeks=6)
            end_date = start_of_week + timedelta(weeks=1)
            completed_lessons = Lesson.objects.filter(
                attended=True,  # Assuming 'attended' field indicates completion
                booked_datetime__gte=start_date,
                booked_datetime__lte=end_date,
                registration__student__user_id=request.user.id
            ).order_by('booked_datetime').annotate(
                week_number=ExtractWeek('booked_datetime')  # Extract the week number from the attended_date
            ).values('week_number').annotate(completed_lessons_count=Count('id'))
            return Response(list(completed_lessons))
        elif progress_type == "monthly":
            today_date = today_date.replace(day=1)
            start_date = today_date - relativedelta(months=5)
            end_date = today_date + relativedelta(months=1)
            completed_lessons = Lesson.objects.filter(
                attended=True,  # Assuming 'attended' field indicates completion
                booked_datetime__gte=start_date,
                booked_datetime__lt=end_date,
                registration__student__user_id=request.user.id
            ).order_by('booked_datetime').annotate(
                month_number=ExtractMonth(F('booked_datetime'), 'doy')  # Extract the week number from the attended_date
            ).values('month_number').annotate(completed_lessons_count=Count('id'))
            return Response(list(completed_lessons))
    
    def recent(self, request):
        filters = {
            "registration__student__user_id": request.user.id
        }
        teacher_uuid = request.data.get("teacher_uuid")
        if teacher_uuid:
            # Assuming you have a Teacher model with a UUID field
            teacher = get_object_or_404(Teacher, user__uuid=teacher_uuid)
            filters['registration__teacher_id'] = teacher.id
        lessons = Lesson.objects.filter(**filters)
        ser = ListLessonDateTimeSerializer(instance=lessons, many=True)
        return Response(ser.data, status=200)
    
    def day(self, request):
        date = request.data.get("date")
        lessons = Lesson.objects.select_related("registration__teacher__user").filter(
            registration__student__user_id=request.user.id,
            booked_datetime__date=date,
        )
        ser = ListLessonSerializer(instance=lessons, many=True)
        return Response(ser.data)
    
    def create(self, request):
        data = dict(request.data)
        data["student_id"] = request.user.id
        ser = LessonSerializer(data=data)
        if ser.is_valid():
            obj = ser.create(validated_data=ser.validated_data)
            return Response({"booked_date": obj.booked_datetime}, status=200)
        else:
            return Response(ser.errors, status=400)
        