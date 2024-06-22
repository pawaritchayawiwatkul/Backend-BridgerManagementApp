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
from django.db.models import Count, F, Func, Value, CharField, Prefetch
from datetime import datetime
from django.db.models.functions import ExtractWeek, Extract, ExtractMonth
from django.core.exceptions import ValidationError
from student.serializers import UnavailableTimeSerializer, ListLessonSerializer, CourseRegistrationSerializer, LessonSerializer, ListTeacherSerializer, ListCourseRegistrationSerializer, ListLessonDateTimeSerializer, ProfileSerializer
from django.shortcuts import get_object_or_404
from dateutil.relativedelta import relativedelta
from collections import defaultdict

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
        
    def add(self, request, teacher_uuid):
        teacher = get_object_or_404(Teacher, user__uuid=teacher_uuid)
        user = request.user
        student = get_object_or_404(Student, user_id=user.id)
        if not student.teacher.filter(id=teacher.id).exists():
            student.teacher.add(teacher)
            student.school.add(teacher.school_id)        
        return Response(status=200)
    
@permission_classes([IsAuthenticated])
class TeacherViewset(ViewSet):
    def list(self, request):
        user = request.user
        teacher = StudentTeacherRelation.objects.select_related("teacher__school", "teacher__user").order_by("favorite_teacher").filter(student__user_id=user.id)
        ser = ListTeacherSerializer(instance=teacher, many=True)
        return Response(ser.data)
    
    def favorite(self, request, code):
        fav = request.GET.get("fav", None)
        if fav in ["0", "1"]:
            fav = bool(int(fav))
            student = get_object_or_404(StudentTeacherRelation, teacher__user__uuid=code, student__user_id=request.user.id)
            student.favorite_teacher = bool(int(fav))
            student.save()
            return Response({"favorite": fav}, status=200)
        else:
            return Response({"error_messages": ["Invalid Request"]}, status=400)
    
@permission_classes([IsAuthenticated])
class CourseViewset(ViewSet):
    def favorite(self, request, code):
        fav = request.GET.get("fav", None)
        if fav in ["0", "1"]:
            fav = bool(int(fav))
            regis = CourseRegistration.objects.get(uuid=code, student__user_id=request.user.id)
            regis.favorite = bool(int(fav))
            regis.save()
            return Response({"favorite": fav}, status=200)
        else:
            return Response({"error_messages": ["Invalid Request"]}, status=400)
    
    def list(self, request):
        teacher_uuid = request.GET.get("teacher_uuid")
        if not teacher_uuid:
            return Response({"error_messages": ["Please Techer ID"]}, status=400)
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
        date_str = request.GET.get("date", None)
        if not date_str:
            return Response({"error_messages": ["Please Provide Date"]}, status=400)
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return Response({"error_message": ["Invalid Date Format"]}, status=400)
        day_number = date.weekday() + 1
        regis = CourseRegistration.objects.select_related('course', 'teacher__school').prefetch_related(
            Prefetch(
                "teacher__unavailable_reg",
                queryset=UnavailableTimeRegular.objects.filter(
                    day=str(day_number)
                ).only("start", "stop"),
                to_attr="regular"
            ),
            Prefetch(
                "teacher__unavailable_once",
                queryset=UnavailableTimeOneTime.objects.filter(
                    date=date
                ).only("start", "stop"),
                to_attr="once"
            ),
        ).get(uuid=code)
        booked_lessons = Lesson.objects.filter(
            status="CON",
            registration__teacher=regis.teacher,
            booked_datetime__date=date
        ).annotate(time=Func(
            F('booked_datetime'),
            Value('HH:MM:SS'),
            function='to_char',
            output_field=CharField()
        )).values_list("time", flat=True)

        unavailable_regular = UnavailableTimeSerializer(regis.teacher.regular, many=True).data
        unavailable_times = UnavailableTimeSerializer(regis.teacher.once, many=True).data
        return Response(data={
            "booked_lessons": {
                "time": list(booked_lessons),
                "duration": regis.course.duration
            },
            "unavailable": list(unavailable_regular) + list(unavailable_times),
            "start": regis.teacher.school.start,
            "stop": regis.teacher.school.stop,
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
    def range(self, request):
        start_of_range = request.GET.get("start")
        end_of_range = request.GET.get("end")
        if start_of_range and end_of_range:
            filters = {
                "registration__student__user_id": request.user.id,
                "booked_datetime__date__range": [start_of_range, end_of_range]
            }
            if request.GET.get("confirmed", "false") == "false":
                filters['status'] = "PEN"
            else:
                filters['status'] = "CON"
            try:
                lessons = Lesson.objects.filter(**filters)
            except ValidationError as e:
                return Response({"error_message": e}, status=400)
            ser = ListLessonSerializer(instance=lessons, many=True)
            return Response(ser.data, status=200)
        else:
            return Response({"error_message": ["Start or end is empty", ]}, status=400)

    def progress(self, request):
        today_date = request.GET.get("date_of_today", "")
        if not today_date:
            return Response({"error_message": ["Please enter today's date", ]}, status=400)
        try:
            today_date = datetime.strptime(today_date, "%Y-%m-%d")
        except ValueError:
            return Response({"error_message": ["Invalid Date Format"]}, status=400)
        start_day = today_date - timedelta(days=today_date.weekday())
        stop_day = start_day + timedelta(days=7)
        completed_lessons = Lesson.objects.filter(
            status="COM",  # Assuming 'attended' field indicates completion
            booked_datetime__gte=start_day,
            booked_datetime__lt=stop_day,
            registration__student__user_id=request.user.id
        ).order_by('booked_datetime').annotate(
            day_number=Extract(F('booked_datetime'), 'dow')  # Extract the week number from the attended_date
        ).values('day_number')
        
        count_dict = defaultdict(int)
        for entry in completed_lessons:
            count_dict[entry["day_number"]] += 1

        return Response(count_dict)
    
    def recent(self, request):
        filters = {
            "registration__student__user_id": request.user.id
        }
        teacher_uuid = request.GET.get("teacher_uuid")
        if teacher_uuid:
            # Assuming you have a Teacher model with a UUID field
            teacher = get_object_or_404(Teacher, user__uuid=teacher_uuid)
            filters['registration__teacher_id'] = teacher.id
        lessons = Lesson.objects.filter(**filters)
        ser = ListLessonDateTimeSerializer(instance=lessons, many=True)
        return Response(ser.data, status=200)
    
    def day(self, request):
        date = request.GET.get('date', None)
        if not date:
            return Response(status=400)
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
    
    def cancel(self, request, code):
        # Fetch the lesson object ensuring it belongs to the requesting user
        try:
            lesson = Lesson.objects.select_related("registration").get(code=code, registration__student__user__id=request.user.id)
        except Lesson.DoesNotExist:
            return Response({'success': "No Course Registration matches the given query."}, status=200)
        # Calculate the difference between now and the lesson's booked datetime
        now = timezone.now()
        time_difference = lesson.booked_datetime - now

        # Ensure the cancellation is at least 24 hours before the class
        if time_difference.total_seconds() >= 24 * 60 * 60:
            lesson.registration.used_lessons -= 1
            lesson.registration.save()
        lesson.status = 'CAN'
        lesson.save()

        return Response({'success': 'Lesson canceled successfully.'}, status=200)
