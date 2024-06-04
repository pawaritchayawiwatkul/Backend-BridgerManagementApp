from django.urls import path , re_path
from student import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'student'

courseView = views.CourseViewset.as_view({
    'get': 'list',
    'post': 'create'
})

courseDetailView = views.CourseViewset.as_view({
    'get': 'retrieve',
})

courseATview = views.CourseViewset.as_view({
    'get': 'get_available_time',
})

lessonView = views.LessonViewset.as_view({
    'post': 'create'
})
lessonDayView = views.LessonViewset.as_view({
    'get': 'day',
})

lessonProgressView = views.LessonViewset.as_view({
    'get': 'progress',
})

lessonRecentView = views.LessonViewset.as_view({
    'get': 'recent',
})

lessonWeekView = views.LessonViewset.as_view({
    'get': 'week',
})

teacherListView = views.TeacherViewset.as_view({
    'get': 'list',
})

profileView = views.ProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})
# Enter URL path below
urlpatterns = format_suffix_patterns([
    path('profile/', profileView, name='course'),

    path('course/', courseView, name='course'),
    path('course/<slug:code>/', courseDetailView, name='course-detail'),
    path('course/<slug:code>/availabletime', courseATview, name='course-available-time'),
    
    path('lesson/', lessonView, name='lesson'),
    path('lesson/week', lessonWeekView, name='lesson-week'),
    path('lesson/day', lessonDayView, name='lesson-day'),
    path('lesson/recent', lessonRecentView, name='lesson-day'),
    path('lesson/progress/<slug:progress_type>', lessonProgressView, name='course-detail'),

    path('teacher/', teacherListView, name='lesson-day'),
])