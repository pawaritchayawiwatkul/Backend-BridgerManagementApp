from django.urls import path , re_path
from teacher import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'teacher'

# courseView = views.CourseViewset.as_view({
#     # 'get': 'list',
#     'post': 'create'
# })

# Enter URL path below
urlpatterns = format_suffix_patterns([
    # path('course/', courseView, name='course'),
])