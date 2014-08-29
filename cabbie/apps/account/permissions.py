from rest_framework.permissions import BasePermission

class AllowPostToAny(BasePermission):
    """
    customized permission
    POST is allowed for anyone, other methods are only allowed to the authorized 
    useful for signup
    """
    def has_permission(self, request, view):
        return (request.method == 'POST' or 
                request.user and request.user.is_authenticated())
