from rest_framework import serializers
from student.models import Lesson, CourseRegistration, Student, StudentTeacherRelation
from teacher.models import Teacher
from school.models import Course
    
class ListTeacherSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="teacher.user.first_name")
    uuid = serializers.CharField(source="teacher.user.uuid")
    email = serializers.CharField(source="teacher.user.email")
    phone_number = serializers.CharField(source="teacher.user.phone_number")
    school_name = serializers.CharField(source="teacher.school.name")

    class Meta:
        model = StudentTeacherRelation
        fields = ("name", "school_name", "email", "phone_number", "uuid", "favorite_teacher")

class ListCourseRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="course.name")
    description = serializers.CharField(source="course.description")
    number_of_lessons = serializers.IntegerField(source="course.number_of_lessons")
    class Meta:
        model = CourseRegistration
        fields = ("name", "description", "used_lessons", "number_of_lessons", "favorite", "uuid")

class ListLessonDateTimeSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField(source="registration.course.duration")
    
    class Meta:
        model = Lesson
        fields = ("booked_datetime", "duration", "attended")

class ListLessonSerializer(serializers.ModelSerializer):
    duration = serializers.IntegerField(source="registration.course.duration")
    teacher_name = serializers.CharField(source="registration.teacher.user.first_name")
    course_name = serializers.CharField(source="registration.course.name")
    
    class Meta:
        model = Lesson
        fields = ("booked_datetime", "duration", "teacher_name", "course_name", "status", "code")

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
        user_id = attrs.pop("student_id")
        teacher_id = attrs.pop("teacher_id")
        course_id = attrs.pop("course_id")
        try: 
            student = Student.objects.get(user__id=user_id)
            teacher = Teacher.objects.get(user__uuid=teacher_id)
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

class LessonSerializer(serializers.Serializer):
    registration_id = serializers.CharField()
    notes = serializers.CharField(max_length=300)
    student_id = serializers.IntegerField()
    booked_datetime = serializers.DateTimeField() # YYYY-MM-DDThh:mm[:ss[.uuuuuu]][+HH:MM|-HH:MM|Z].
    # Should we add a feature that prevents booking lesser than 1 day in advance?? [ ASK CUSTOMER ]
    def create(self, validated_data):
        return Lesson.objects.create(**validated_data)

    def validate(self, attrs):
        user_id = attrs.pop("student_id")
        registration_id = attrs.pop("registration_id")
        try: 
            course = CourseRegistration.objects.get(uuid=registration_id, student__user_id=user_id)
            attrs['registration_id'] = course.id
        except Student.DoesNotExist:
            raise serializers.ValidationError({
                'student_id': 'User not found'
            })
        except CourseRegistration.DoesNotExist:
            raise serializers.ValidationError({
                'registration_id': 'Teacher not found'
            })
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)
    phone_number = serializers.CharField(source="user.phone_number", required=False)
    uuid = serializers.CharField(source="user.uuid", required=False)
    email = serializers.CharField(source="user.email", required=False)

    class Meta:
        model = Student
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
        
class UnavailableTimeSerializer(serializers.Serializer):
    start = serializers.TimeField()
    stop = serializers.TimeField()

    class Meta:
        fields = ("start", "stop")
