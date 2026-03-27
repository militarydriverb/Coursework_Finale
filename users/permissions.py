from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором.
    """

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()

    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name="Модераторы").exists()


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем объекта.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Разрешает доступ модераторам или владельцам объекта.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # Модератор или владелец
        is_moderator = request.user.groups.filter(name="Модераторы").exists()
        is_owner = obj.owner == request.user
        return is_moderator or is_owner


class IsNotModerator(permissions.BasePermission):
    """
    Разрешает доступ только НЕ-модераторам (обычным пользователям).
    """

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Модераторы").exists()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование только владельцу, просмотр всем.
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Изменение только владельцу
        return obj.owner == request.user
