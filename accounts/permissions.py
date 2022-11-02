from rest_framework import permissions


def is_driver(obj):
    """
    Checks if user is driver
    """
    if hasattr(obj, 'driver'):
        return True
    return False


def is_admin(obj):
    """
    checks if user is admin
    """
    if hasattr(obj, 'admin'):
        return True
    return False


class IsDriver(permissions.BasePermission):
    """
    Grants permission users who are also driver
    """
    def has_permission(self, request, view):
        user = request.user
        return is_driver(user)


class IsVerifiedDriver(permissions.BasePermission):
    """
    Grants permission to users who have verified driver account
    """
    def has_permission(self, request, view):
        user = request.user
        if is_driver(user):
            return user.driver.status == 'verified'
        return False


class IsAdmin(permissions.BasePermission):
    """
    Grants permission to users who have admin privilege.
    """
    def has_permission(self, request, view):
        return is_admin(request.user)


class IsNotBlacklisted(permissions.BasePermission):
    """
    Grants permission to user who are not blacklisted.
    """
    def has_permission(self, request, view):
        return request.user.blacklisted == False

