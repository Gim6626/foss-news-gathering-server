from rest_framework import (
    permissions,
)


class TelegramBotReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.username == 'tbot' and request.method in permissions.SAFE_METHODS


class TelegramBotFullPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.username == 'tbot'
