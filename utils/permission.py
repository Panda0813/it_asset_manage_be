from rest_framework.permissions import BasePermission


SAFE_METHODS = ('GET', 'HEADS', 'OPTIONS')


class IsNotLogin(BasePermission):
    """
    允许未登录的用户操作
    """
    def has_permission(self, request, view):
        return True


class IsActiveUser(BasePermission):
    """
    允许启用的用户、超管
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_active or
                    request.user.is_superuser or
                    request.GET.get('from_path') == 'register')


class IsActiveUserOrReadOnly(BasePermission):
    """
    允许的请求、启用的用户、超管
    """
    def has_permission(self, request, view):
        return bool(request.method in SAFE_METHODS or
                    request.user and
                    request.user.is_active or
                    request.user.is_superuser)


class IsSuperUser(BasePermission):
    """
    只允许超管
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class IsSuperUserOrReadOnly(BasePermission):
    """
    超管操作或者只能是允许的请求
    """
    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_superuser
        )
