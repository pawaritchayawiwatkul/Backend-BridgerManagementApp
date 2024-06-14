from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from teacher.models import Teacher, TeacherCourses
from teacher.serializers import RegularUnavailableSerializer, OnetimeUnavailableSerializer, UnavailableTimeOneTime, UnavailableTimeRegular, TeacherCourseListSerializer, CourseSerializer, ProfileSerializer, ListStudentSerializer, ListCourseRegistrationSerializer, ListLessonDateTimeSerializer, CourseRegistrationSerializer, ListLessonSerializer
from student.models import Student, StudentTeacherRelation, CourseRegistration, Lesson
from django.core.exceptions import ValidationError
from rest_framework.views import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from datetime import timedelta, datetime
from django.db.models import Count, F
from django.db.models.functions import ExtractWeek, Extract, ExtractMonth
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from utils import merge_schedule, split_at_reg
@permission_classes([IsAuthenticated])
class UnavailableTimeViewset(ViewSet):
    def one_time(self, request):
        data = request.data
        data['user_id'] = request.user.id
        ser = OnetimeUnavailableSerializer(data=data)
        if ser.is_valid():
            date = ser.validated_data['date']
            teacher_id = ser.validated_data['teacher_id']
            unavailables = list(UnavailableTimeOneTime.objects.filter(date=date, teacher_id=teacher_id).only("start", "stop"))
            validated_data, overlap = merge_schedule(ser.validated_data, unavailables)
            ids_to_delete = [int(instance.id) for instance in overlap]
            UnavailableTimeOneTime.objects.filter(id__in=ids_to_delete).delete()
            ser.create(validated_data)
            return Response(ser.data, status=200)
        return Response(ser.errors, status=400)
    
    def regular(self, request):
        data = request.data
        data['user_id'] = request.user.id
        ser = RegularUnavailableSerializer(data=data)
        if ser.is_valid():
            day = ser.validated_data['day']
            teacher_id = ser.validated_data['teacher_id']
            unavailables = list(UnavailableTimeRegular.objects.filter(day=day, teacher_id=teacher_id).only("start", "stop"))
            validated_data, overlap = merge_schedule(ser.validated_data, unavailables)
            ids_to_delete = [int(instance.id) for instance in overlap]
            UnavailableTimeRegular.objects.filter(id__in=ids_to_delete).delete()
            ser.create(validated_data)
            return Response(ser.data, status=200)
        return Response(ser.errors, status=400)
    
@permission_classes([IsAuthenticated])
class CourseViewset(ViewSet):
    def list(self, request):
        teacher_course = TeacherCourses.objects.select_related("course").filter(teacher__user_id=request.user.id)
        ser = TeacherCourseListSerializer(instance=teacher_course, many=True)
        return Response(ser.data)
    
    def create(self, request):
        data = dict(request.data)
        data["user_id"] = request.user.id
        ser = CourseSerializer(data=data)
        if ser.is_valid():
            ser.create(validated_data=ser.validated_data)
            return Response(ser.data, status=200)
        else:
            return Response(ser.errors, status=400)
    
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
    

@permission_classes([IsAuthenticated])
class StudentViewset(ViewSet):
    def list(self, request):
        user = request.user
        students = StudentTeacherRelation.objects.select_related("student__user").filter(teacher__user_id=user.id)
        ser = ListStudentSerializer(instance=students, many=True)
        return Response(ser.data)
    
@permission_classes([IsAuthenticated]) 
class RegistrationViewset(ViewSet):
    def list(self, request):
        student_uuid = request.GET.get("student_uuid")
        if not student_uuid:
            return Response({"error_messages": ["Please Student UUID"]}, status=400)
        filters = {
            'teacher__user_id': request.user.id,
        }
        if request.data.get("all_course"):
            filters['completed'] = True
        else:
            filters['completed'] = False

        if student_uuid:
            # Assuming you have a Teacher model with a UUID field
            student = get_object_or_404(Student, user__uuid=student_uuid)
            filters['student'] = student

        courses = CourseRegistration.objects.select_related("course").filter(**filters)
        ser = ListCourseRegistrationSerializer(instance=courses, many=True)
        return Response(ser.data)
    
    def retrieve(self, request, code):
        filters = {
            "registration__uuid": code,
            "registration__teacher__user_id": request.user.id
        }
        lessons = Lesson.objects.filter(**filters)
        ser = ListLessonDateTimeSerializer(instance=lessons, many=True)
        return Response(ser.data, status=200)
    
    def create(self, request):
        data = dict(request.data)
        data["teacher_id"] = request.user.id
        ser = CourseRegistrationSerializer(data=data)
        if ser.is_valid():
            obj = ser.create(validated_data=ser.validated_data)
            return Response({"registration_id": obj.uuid}, status=200)
        else:
            return Response(ser.errors, status=400)

@permission_classes([IsAuthenticated])
class LessonViewset(ViewSet):
    def range(self, request):
        start_of_range = request.GET.get("start")
        end_of_range = request.GET.get("end")
        if start_of_range and end_of_range:
            filters = {
                "registration__teacher__user_id": request.user.id,
                "booked_datetime__date__range": [start_of_range, end_of_range]
            }
            if request.GET.get("confirmed", "false") == "false":
                filters['confirmed'] = False
            else:
                filters['confirmed'] = True
            try:
                lessons = Lesson.objects.filter(**filters)
            except ValidationError as e:
                return Response({"error_message": e}, status=400)
            ser = ListLessonSerializer(instance=lessons, many=True)
            return Response(ser.data, status=200)
        else:
            return Response({"error_message": ["Start or end is empty", ]}, status=400)

    def confirm(self, request):
        return Response()
    
    def progress(self, request, progress_type):
        today_date = request.GET.get("date_of_today", "")
        if not today_date:
            return Response({"error_message": ["Please enter today's date", ]}, status=400)
        try:
            today_date = datetime.strptime(today_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error_message": ["Invalid Date Format"]}, status=400)
        if progress_type == "daily":
            seven_days_ago = today_date - timedelta(days=7)
            stop_day = today_date + timedelta(days=1)
            completed_lessons = Lesson.objects.filter(
                attended=True,  # Assuming 'attended' field indicates completion
                booked_datetime__gte=seven_days_ago,
                booked_datetime__lt=stop_day,
                registration__teacher__user_id=request.user.id
            ).order_by('booked_datetime').annotate(
                day_number=Extract(F('booked_datetime'), 'doy')  # Extract the week number from the attended_date
            ).values('day_number')

            count_dict = defaultdict(int)
            for entry in completed_lessons:
                count_dict[entry["day_number"]] += 1

            return Response(count_dict)
        elif progress_type == "weekly":
            start_of_week = today_date - timedelta(days=today_date.weekday())  # Assuming Monday is the start of the week
            start_date = today_date - timedelta(weeks=6)
            end_date = start_of_week + timedelta(weeks=1)
            completed_lessons = Lesson.objects.filter(
                attended=True,  # Assuming 'attended' field indicates completion
                booked_datetime__gte=start_date,
                booked_datetime__lte=end_date,
                registration__teacher__user_id=request.user.id
            ).order_by('booked_datetime').annotate(
                week_number=ExtractWeek('booked_datetime')  # Extract the week number from the attended_date
            ).values('week_number')
            
            count_dict = defaultdict(int)
            for entry in completed_lessons:
                count_dict[entry["week_number"]] += 1

            return Response(count_dict)
        elif progress_type == "monthly":
            today_date = today_date.replace(day=1)
            start_date = today_date - relativedelta(months=5)
            end_date = today_date + relativedelta(months=1)
            completed_lessons = Lesson.objects.filter(
                attended=True,  # Assuming 'attended' field indicates completion
                booked_datetime__gte=start_date,
                booked_datetime__lt=end_date,
                registration__teacher__user_id=request.user.id
            ).order_by('booked_datetime').annotate(
                month_number=ExtractMonth(F('booked_datetime'), 'doy')  # Extract the week number from the attended_date
            ).values('month_number')

            count_dict = defaultdict(int)
            for entry in completed_lessons:
                count_dict[entry["month_number"]] += 1

            return Response(count_dict)
        return Response("invalid choice", status=400)
    
    def recent(self, request):
        filters = {
            "registration__teacher__user_id": request.user.id
        }
        student_uuid = request.GET.get("student_uuid")
        if student_uuid:
            # Assuming you have a Teacher model with a UUID field
            student = get_object_or_404(Student, user__uuid=student_uuid)
            filters['registration__student_id'] = student.id
        lessons = Lesson.objects.filter(**filters)
        ser = ListLessonDateTimeSerializer(instance=lessons, many=True)
        return Response(ser.data, status=200)
    
    def day(self, request):
        date = request.GET.get('date', None)
        if not date:
            return Response(status=400)
        lessons = Lesson.objects.select_related("registration__student__user").filter(
            registration__teacher__user_id=request.user.id,
            booked_datetime__date=date,
        )
        ser = ListLessonSerializer(instance=lessons, many=True)
        return Response(ser.data)
