from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment, User
from users.serializers import PaymentSerializer, UserPublicSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        # Регистрация доступна всем
        if self.action == "create":
            self.permission_classes = [AllowAny]
        # Остальные действия требуют авторизации
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        # Если пользователь смотрит чужой профиль - показываем публичную версию
        if self.action == "retrieve" and self.get_object() != self.request.user:
            return UserPublicSerializer
        return UserSerializer

    def get_queryset(self):
        # Для update и partial_update - только свой профиль
        if self.action in ["update", "partial_update", "destroy"]:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
