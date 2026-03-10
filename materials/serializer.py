from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from materials.models import Course, Lesson, Subscription, Payment
from materials.validators import validate_youtube_url


class LessonSerializer(ModelSerializer):
    video_url = serializers.URLField(validators=[validate_youtube_url])

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(source='lesson_set', many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, obj):
        return obj.lesson_set.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Subscription.objects.filter(user=user, course=obj).exists()
        return False


class PaymentSerializer(ModelSerializer):
    """Сериализатор для модели Payment"""

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'course', 'amount', 'stripe_product_id',
            'stripe_price_id', 'stripe_session_id', 'payment_url',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'stripe_product_id', 'stripe_price_id',
            'stripe_session_id', 'payment_url', 'status',
            'created_at', 'updated_at'
        ]


class PaymentCreateSerializer(ModelSerializer):
    """Сериализатор для создания платежа"""

    class Meta:
        model = Payment
        fields = ['course']

    def validate_course(self, value):
        """Проверяем, что курс имеет цену"""
        if value.price <= 0:
            raise serializers.ValidationError("Курс должен иметь цену больше 0")
        return value


class PaymentStatusSerializer(serializers.Serializer):
    """Сериализатор для получения статуса платежа"""
    session_id = serializers.CharField(required=True, help_text="ID сессии Stripe")
    status = serializers.CharField(read_only=True, help_text="Статус платежа")
    payment_status = serializers.CharField(read_only=True, help_text="Статус оплаты в Stripe")