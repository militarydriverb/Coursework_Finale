from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView, get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, Lesson, Subscription
from materials.paginators import CustomPagination
from materials.serializer import CourseSerializer, LessonSerializer
from users.permissions import IsModeratorOrOwner, IsNotModerator, IsOwner


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Модераторы видят все курсы.
        Обычные пользователи видят только свои курсы.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == 'create':
            # Создавать могут только не-модераторы
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action == 'destroy':
            # Удалять могут только владельцы (не модераторы)
            self.permission_classes = [IsAuthenticated, IsNotModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            # Редактировать могут модераторы или владельцы
            self.permission_classes = [IsAuthenticated, IsModeratorOrOwner]
        else:
            # List, retrieve - все авторизованные (но queryset ограничен)
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(ListAPIView):
    serializer_class = LessonSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Модераторы видят все уроки.
        Обычные пользователи видят только свои уроки.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Модераторы видят все уроки.
        Обычные пользователи видят только свои уроки.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonCreateAPIView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsNotModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonUpdateAPIView(UpdateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModeratorOrOwner]

    def get_queryset(self):
        """
        Модераторы видят все уроки.
        Обычные пользователи видят только свои уроки.
        """
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(DestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsNotModerator, IsOwner]

    def get_queryset(self):
        """
        Только владелец может удалить свой урок.
        """
        return Lesson.objects.filter(owner=self.request.user)


class SubscriptionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.all()

    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course')
        course_item = get_object_or_404(Course, pk=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})
