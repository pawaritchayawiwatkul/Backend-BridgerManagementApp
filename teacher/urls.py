from django.urls import path , re_path
from teacher import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'teacher'

profileAddView = views.ProfileViewSet.as_view({
    'post': 'add'
})

profileView = views.ProfileViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})


# Enter URL path below
urlpatterns = format_suffix_patterns([
    path('profile/', profileView, name='profile'),
    path('profile/add/<slug:student_uuid>', profileAddView, name='profile-add'),
])