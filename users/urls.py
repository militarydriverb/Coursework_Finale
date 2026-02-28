from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import PaymentViewSet, UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
