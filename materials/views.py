from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
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

from materials.models import Course, Lesson, Subscription, Payment
from materials.paginators import CustomPagination
from materials.serializer import (
    CourseSerializer, LessonSerializer, PaymentSerializer,
    PaymentCreateSerializer, PaymentStatusSerializer
)
from materials.services import (
    create_stripe_product, create_stripe_price,
    create_stripe_session, retrieve_stripe_session
)
from materials.tasks import send_course_update_email
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

    def perform_update(self, serializer):
        """Переопределяем метод обновления для отправки уведомлений подписчикам"""
        course = self.get_object()

        # Проверяем, прошло ли более 4 часов с последнего обновления
        four_hours_ago = timezone.now() - timedelta(hours=4)
        should_send_notification = course.updated_at < four_hours_ago

        # Сохраняем обновления
        serializer.save()

        # Если прошло более 4 часов, отправляем уведомления подписчикам
        if should_send_notification:
            subscriptions = Subscription.objects.filter(course=course)
            for subscription in subscriptions:
                # Вызываем асинхронную задачу через Celery
                send_course_update_email.delay(
                    course_name=course.name,
                    user_email=subscription.user.email
                )


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

    def perform_update(self, serializer):
        """Переопределяем метод обновления урока для отправки уведомлений о курсе"""
        lesson = self.get_object()

        # Сохраняем обновления урока
        serializer.save()

        # Если урок привязан к курсу, проверяем необходимость отправки уведомлений
        if lesson.course:
            course = lesson.course
            # Проверяем, прошло ли более 4 часов с последнего обновления курса
            four_hours_ago = timezone.now() - timedelta(hours=4)
            should_send_notification = course.updated_at < four_hours_ago

            if should_send_notification:
                # Обновляем время обновления курса
                course.save()

                # Отправляем уведомления подписчикам курса
                subscriptions = Subscription.objects.filter(course=course)
                for subscription in subscriptions:
                    # Вызываем асинхронную задачу через Celery
                    send_course_update_email.delay(
                        course_name=course.name,
                        user_email=subscription.user.email
                    )


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


class PaymentViewSet(ModelViewSet):
    """ViewSet для работы с платежами"""
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Пользователи видят только свои платежи"""
        return Payment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """Используем разные сериализаторы для разных действий"""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'check_status':
            return PaymentStatusSerializer
        return PaymentSerializer

    def create(self, request, *args, **kwargs):
        """Создание платежа и получение ссылки на оплату"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course = serializer.validated_data['course']
        user = request.user

        try:
            # Создаем продукт в Stripe
            stripe_product = create_stripe_product(
                name=course.name,
                description=course.description
            )

            # Создаем цену в Stripe
            stripe_price = create_stripe_price(
                product_id=stripe_product['id'],
                amount=course.price
            )

            # Создаем сессию для оплаты
            # URL для успешной оплаты и отмены (можно настроить под ваш проект)
            success_url = request.build_absolute_uri('/api/payments/success/')
            cancel_url = request.build_absolute_uri('/api/payments/cancel/')

            stripe_session = create_stripe_session(
                price_id=stripe_price['id'],
                success_url=success_url,
                cancel_url=cancel_url
            )

            # Создаем платеж в нашей системе
            payment = Payment.objects.create(
                user=user,
                course=course,
                amount=course.price,
                stripe_product_id=stripe_product['id'],
                stripe_price_id=stripe_price['id'],
                stripe_session_id=stripe_session['id'],
                payment_url=stripe_session['url'],
                status='pending'
            )

            # Возвращаем данные о платеже
            response_serializer = PaymentSerializer(payment)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Ошибка при создании платежа: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], url_path='check-status')
    def check_status(self, request):
        """
        Проверка статуса платежа по session_id
        Эндпоинт: POST /api/payments/check-status/
        Параметры: {"session_id": "cs_test_..."}
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data['session_id']

        try:
            # Получаем данные о сессии из Stripe
            stripe_session = retrieve_stripe_session(session_id)

            # Обновляем статус платежа в нашей системе
            payment = Payment.objects.filter(stripe_session_id=session_id).first()
            if payment:
                if stripe_session['payment_status'] == 'paid':
                    payment.status = 'completed'
                elif stripe_session['payment_status'] == 'unpaid':
                    payment.status = 'pending'
                else:
                    payment.status = 'failed'
                payment.save()

            # Возвращаем информацию о статусе
            return Response({
                'session_id': session_id,
                'payment_status': stripe_session['payment_status'],
                'status': payment.status if payment else 'unknown',
                'amount_total': stripe_session.get('amount_total', 0) / 100,  # конвертируем из копеек
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Ошибка при проверке статуса: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
