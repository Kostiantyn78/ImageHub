from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        The __call__ function is the function that will be called when a user tries to access this endpoint.
        It takes in two parameters: request and user. The request parameter is an object containing information about the HTTP Request, such as headers, body, etc.
        The user parameter is an object containing information about the current logged-in User (if any). This value comes from auth_service's get_current_user() function.

        :param self: Access the class attributes
        :param request: Request: Get the request object
        :param user: User: Get the current user from the auth_service
        :return: A function that is decorated with the @permission_required decorator
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
