"""Rotas de autenticação: cadastro, login, refresh, logout e perfil."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from app.api.deps import (
    EmailSender,
    get_auth_service,
    get_current_user,
    get_email_sender,
    get_verification_email_sender,
)
from app.core.config import get_settings
from app.core.constants import (
    EMAIL_VERIFICATION_PATH,
    ERR_EMAIL_ALREADY_REGISTERED,
    ERR_EMAIL_NOT_VERIFIED,
    ERR_INVALID_CREDENTIALS,
    ERR_INVALID_TOKEN,
    MSG_EMAIL_VERIFIED,
    MSG_PASSWORD_RESET_SENT,
    MSG_PASSWORD_RESET_SUCCESS,
    MSG_REGISTER_CONFIRMATION_SENT,
    PASSWORD_RESET_PATH,
    REFRESH_TOKEN_COOKIE_NAME,
)
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserPublic
from app.services.auth_service import AuthService
from app.services.exceptions import (
    EmailAlreadyRegisteredError,
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidTokenError,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_SECONDS_PER_DAY = 86_400


def _set_refresh_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=settings.jwt_refresh_token_expire_days * _SECONDS_PER_DAY,
        path="/auth",
    )


def _build_token_response(response: Response, service: AuthService, user: User) -> TokenResponse:
    _set_refresh_cookie(response, service.issue_refresh_token(user))
    return TokenResponse(access_token=service.issue_access_token(user), user=user.to_public())


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    email_sender: Annotated[EmailSender, Depends(get_verification_email_sender)],
) -> MessageResponse:
    try:
        user = await service.register(payload)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=ERR_EMAIL_ALREADY_REGISTERED,
        ) from None

    # Conta criada inativa: envia o link de confirmação (válido por 24h).
    token = service.issue_email_verification_token(user)
    verify_link = f"{get_settings().frontend_origin}{EMAIL_VERIFICATION_PATH}?token={token}"
    await email_sender(user.email, verify_link)
    return MessageResponse(message=MSG_REGISTER_CONFIRMATION_SENT)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    try:
        user = await service.authenticate(payload)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_CREDENTIALS,
        ) from None
    except EmailNotVerifiedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERR_EMAIL_NOT_VERIFIED,
        ) from None
    return _build_token_response(response, service, user)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    payload: VerifyEmailRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    try:
        await service.verify_email(payload.token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERR_INVALID_TOKEN,
        ) from None
    return MessageResponse(message=MSG_EMAIL_VERIFIED)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_TOKEN_COOKIE_NAME)] = None,
) -> TokenResponse:
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERR_INVALID_TOKEN)
    try:
        user = await service.user_from_refresh_token(refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERR_INVALID_TOKEN,
        ) from None
    return _build_token_response(response, service, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(REFRESH_TOKEN_COOKIE_NAME, path="/auth")


@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    payload: ForgotPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
) -> MessageResponse:
    token = await service.create_password_reset_token(payload.email)
    if token is not None:
        reset_link = f"{get_settings().frontend_origin}{PASSWORD_RESET_PATH}?token={token}"
        await email_sender(payload.email, reset_link)
    # Mensagem genérica independente de o e-mail existir (evita enumeração).
    return MessageResponse(message=MSG_PASSWORD_RESET_SENT)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    try:
        await service.reset_password(payload.token, payload.password)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERR_INVALID_TOKEN,
        ) from None
    return MessageResponse(message=MSG_PASSWORD_RESET_SUCCESS)


@router.get("/me", response_model=UserPublic)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserPublic:
    return current_user.to_public()
