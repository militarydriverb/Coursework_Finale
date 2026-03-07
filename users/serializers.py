from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from materials.models import Subscription
from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    # Выводим название курса вместо его ID
    course_name = serializers.ReadOnlyField(source='course.name')

    class Meta:
        model = Subscription
        fields = ['course', 'course_name']


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    subscription = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "tg_nick",
            "avatar",
            "payments",
            "subscription",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)

    def get_subscription(self, instance):
        # instance — это объект пользователя (User)
        # Получаем все подписки этого пользователя
        return [sub.course.name for sub in instance.subscription_set.all()]


class UserPublicSerializer(serializers.ModelSerializer):
    """Сериализатор для публичного профиля (без чувствительных данных)"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "phone",
            "tg_nick",
            "avatar",
        ]
        read_only_fields = fields
