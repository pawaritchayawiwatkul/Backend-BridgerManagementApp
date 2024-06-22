from django.urls import path , re_path
from teacher import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'teacher'

profileAddView = views.ProfileViewSet.as_view({
    'post': 'add',
    # 'get': 'list'
})

profileView = views.ProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})

courseView = views.CourseViewset.as_view({
    'get': 'list',
    'post': 'create'
})

courseDetailView = views.CourseViewset.as_view({
    'get': 'retrieve',
})

lessonProgressView = views.LessonViewset.as_view({
    "get": "progress"
})

lessonDayView = views.LessonViewset.as_view({
    'get': 'day',
})

lessonWeekView = views.LessonViewset.as_view({
    'get': 'week',
})

LessonCancelView = views.LessonViewset.as_view({
    'put': 'cancel',
})

LessonConfirmView = views.LessonViewset.as_view({
    'put': 'confirm',
})

lessonRecentView = views.LessonViewset.as_view({
    'get': 'recent',
})


studentListView = views.StudentViewset.as_view({
    'get': 'list'
})

registrationView = views.RegistrationViewset.as_view({
    'get': 'list'
})

registrationDetailView = views.RegistrationViewset.as_view({
    'get': 'retrieve'
})

oneTimeUnavailable = views.UnavailableTimeViewset.as_view({
    'post': 'one_time'
})

regularUnavailable = views.UnavailableTimeViewset.as_view({
    'post': 'regular'
})
# Enter URL path below
urlpatterns = format_suffix_patterns([
    path('profile/', profileView, name='profile'),
    path('profile/add/<slug:student_uuid>', profileAddView, name='profile-add'),
    path('course/', courseView, name='course'),
    path('course/<slug:code>', courseDetailView, name='course'),

    path('registration/', registrationView, name='course'),
    path('registration/<slug:code>', registrationDetailView, name='course'),

    path('lesson/day', lessonDayView, name='lesson-day'),
    path('lesson/week', lessonWeekView, name='lesson-week'),
    path('lesson/progress', lessonProgressView, name='lesson-progress'),
    path('lesson/recent', lessonRecentView, name='lesson-recent'),
    path('lesson/<slug:code>/cancel', LessonCancelView, name='lesson-progress'),
    path('lesson/<slug:code>/confirm', LessonConfirmView, name='lesson-progress'),

    path('unavailable/onetime', oneTimeUnavailable, name='unavailable-onetime'),
    path('unavailable/regular', regularUnavailable, name='unavailable-regular'),

    path('student', studentListView, name='student-list'),
])