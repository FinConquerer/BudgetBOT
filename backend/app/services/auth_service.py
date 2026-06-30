"""Service xử lý nghiệp vụ Auth/User."""

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import (
    DuplicateUserError,
    UserRecord,
    UserRepository,
)
from app.schemas import (
    LoginResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    TokenUserResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Nghiệp vụ đăng ký, đăng nhập và lấy user hiện tại."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register(self, request: UserRegisterRequest) -> UserResponse:
        if self.user_repository.get_by_username(request.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists",
            )
        if request.email and self.user_repository.get_by_email(request.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        try:
            user = self.user_repository.create_user(
                username=request.username,
                email=request.email,
                password_hash=hash_password(request.password),
            )
        except DuplicateUserError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username or email already exists",
            ) from exc

        return self._user_response(user)

    def login(self, request: UserLoginRequest) -> LoginResponse:
        user = self.user_repository.get_by_username(request.username)
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        access_token, expires_in = create_access_token(subject=user.id)
        return LoginResponse(
            access_token=access_token,
            expires_in=expires_in,
            user=TokenUserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
            ),
        )

    def reset_password(self, request: PasswordResetRequest) -> PasswordResetResponse:
        """Đặt lại mật khẩu khi username + email khớp một tài khoản đang hoạt động.

        Chưa có hạ tầng gửi email nên dùng email như yếu tố xác minh. Trả lỗi chung
        để không tiết lộ tài khoản nào tồn tại.
        """
        invalid = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username và email không khớp tài khoản nào",
        )
        user = self.user_repository.get_by_username(request.username)
        if not user or not user.email or user.email.lower() != request.email.lower():
            raise invalid
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
            )

        self.user_repository.update_password(user.id, hash_password(request.new_password))
        return PasswordResetResponse(success=True)

    def get_current_user(self, token: str) -> UserRecord:
        payload = decode_access_token(token)
        user_id = payload.get("sub") if payload else None
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        user = self.user_repository.get_by_id(str(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        return user

    def _user_response(self, user: UserRecord) -> UserResponse:
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
