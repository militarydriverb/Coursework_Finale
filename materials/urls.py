from django.urls import path
from rest_framework.routers import SimpleRouter

from materials.apps import MaterialsConfig
from materials.views import (LessonCreateApiView, LessonListApiView,
                             LessonRetrieveUpdateDestroyAPIView, CourseViewSet)

app_name = MaterialsConfig.name

router = SimpleRouter()
router.register("courses", CourseViewSet, basename="courses")


urlpatterns = [
    path("lessons/", LessonListApiView.as_view(), name="lesson-list"),
    path("lessons/create/", LessonCreateApiView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/", LessonRetrieveUpdateDestroyAPIView.as_view(), name="lesson-update"),
]

urlpatterns += router.urls