from rest_framework import serializers
from teacher.models import Course, Teacher, TeacherCourses, UnavailableTimeOneTime, UnavailableTimeRegular
from student.models import StudentTeacherRelation, CourseRegistration, Lesson, Student
from datetime import datetime

class RegularUnavailableSerializer(serializers.ModelSerializer):
    day = serializers.ChoiceField(choices=UnavailableTimeRegular.DAY_CHOICES)
    start = serializers.TimeField()
    stop = serializers.TimeField()
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UnavailableTimeRegular
        fields = ("day", "start", "stop", "user_id")

    def create(self, validated_data):
        return UnavailableTimeRegular.objects.get_or_create(**validated_data)
    
    def validate(self, attrs):
        user_id = attrs.pop('user_id')
        try:
            teacher = Teacher.objects.get(user_id=user_id)
            attrs['teacher_id'] = teacher.id
        except Teacher.DoesNotExist:
            raise serializers.ValidationError({
                'user_id': 'Teacher not found'
            })
        if attrs['stop'] < attrs['start']:
            raise serializers.ValidationError({
                'start_n_stop': 'start must be before stop'
            })
        return attrs

class OnetimeUnavailableSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    start = serializers.TimeField()
    stop = serializers.TimeField()
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UnavailableTimeOneTime
        fields = ("date", "start", "stop", "user_id")
                  
    def create(self, validated_data):
        return UnavailableTimeOneTime.objects.get_or_create(**validated_data)
    
    def validate(self, attrs):
        user_id = attrs.pop('user_id')
        try:
            teacher = Teacher.objects.get(user_id=user_id)
            attrs['teacher_id'] = teacher.id
        except Teacher.DoesNotExist:
            raise serializers.ValidationError({
                'user_id': 'Teacher not found'
            })
        if attrs['stop'] < attrs['start']:
            raise serializers.ValidationError({
                'start_n_stop': 'start must be before stop'
            })
        return attrs

class TeacherCourseListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="course.name")
    description = serializers.CharField(source="course.description")
    no_exp = serializers.BooleanField(source="course.no_exp")
    exp_range = serializers.IntegerField(source="course.exp_range")
    duration = serializers.IntegerField(source="course.duration")
    number_of_lessons = serializers.IntegerField(source="course.number_of_lessons")

    class Meta:
        model = TeacherCourses
        fields = ("name", "description", "no_exp", "exp_range", "duration", "number_of_lessons", "favorite")

class CourseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=300)
    no_exp = serializers.BooleanField(default=True)
    exp_range = serializers.IntegerField(required=False)
    duration = serializers.IntegerField()
    number_of_lessons = serializers.IntegerField()
    user_id = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        print(validated_data)
        return Course.objects.create(**validated_data)

    def validate(self, attrs):
        no_exp = attrs.get('no_exp')
        exp_range = attrs.get('exp_range')
        if not no_exp and not exp_range:
            raise serializers.ValidationError({
                'exp_range': 'This field is required when no_exp is False.'
            })
        
        user_id = attrs.pop("user_id")
        try: 
            teacher = Teacher.objects.select_related("school").get(user__id=user_id)
            attrs['school_id'] = teacher.school.id
        except Teacher.DoesNotExist:
            raise serializers.ValidationError({
                'user_id': 'User not found'
            })
        return attrs
    
class ListStudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="student.user.first_name")
    phone_number = serializers.CharField(source="student.user.phone_number")
    email = serializers.CharField(source="student.user.email")
    uuid = serializers.CharField(source="student.user.uuid")

    class Meta:
        model = StudentTeacherRelation
        fields = ("name", "phone_number", "email", "uuid", "favorite_student")

class ListCourseRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="course.name")
    description = serializers.CharField(source="course.description")
    number_of_lessons = serializers.IntegerField(source="course.number_of_lessons")
    class Meta:
        model = CourseRegistration
        fields = ("name", "description", "used_lessons", "number_of_lessons", "favorite", "uuid")

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
    
class ListLessonDateTimeSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField(source="registration.course.duration")
    
    class Meta:
        model = Lesson
        fields = ("booked_datetime", "duration", "attended")

class CourseRegistrationSerializer(serializers.Serializer):
    course_id = serializers.CharField()
    teacher_id = serializers.CharField()
    student_id = serializers.IntegerField()

    def create(self, validated_data):
        regis = CourseRegistration.objects.create(**validated_data)
        student = validated_data['student']
        teacher = validated_data['teacher']
        if not student.teacher.filter(id=teacher.id).exists():
            student.teacher.add(teacher)
            student.school.add(teacher.school_id)
        return regis
    
    def validate(self, attrs):
        student_id = attrs.pop("student_id")
        user_id = attrs.pop("teacher_id")
        course_id = attrs.pop("course_id")
        try: 
            student = Student.objects.get(user__uuid=student_id)
            teacher = Teacher.objects.get(user__id=user_id)
            course = Course.objects.get(uuid=course_id)
            attrs['student'] = student
            attrs['teacher'] = teacher
            attrs['course_id'] = course.id
        except Student.DoesNotExist:
            raise serializers.ValidationError({
                'user_id': 'User not found'
            })
        except Teacher.DoesNotExist:
            raise serializers.ValidationError({
                'teacher_code': 'Teacher not found'
            })
        except Course.DoesNotExist:
            raise serializers.ValidationError({
                'course_code': 'Course not found'
            })
        return attrs

class ListLessonSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField(source="registration.course.duration")
    student_name = serializers.CharField(source="registration.student.user.first_name")
    course_name = serializers.CharField(source="registration.course.name")
    
    class Meta:
        model = Lesson
        fields = ("booked_datetime", "duration", "student_name", "course_name", "code")
