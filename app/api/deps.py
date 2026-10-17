from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.domain.models import CurrentUser


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_email: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
) -> CurrentUser:
    if not x_user_id or not x_user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identidad no provista por APIM")
    return CurrentUser(user_id=x_user_id, email=x_user_email, role=x_user_role)


CurrentUserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere rol admin")
    return user
