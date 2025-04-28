import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.db.db import engine
from src.db.db_init import init_db
from src.routers import auth, users, orders, products, categories, reviews, cart, payments
from src.custom_exceptions import (
    PetStoreApiError,
    ResourceDoesNotExistError,
    ResourceAlreadyExistsError,
    NotEnoughRightsError,
    InvalidTokenError,
    InvalidCredentialsError,
    FileTooLargeError,
    NotSupportedFileTypeError,
    LimitExceededError,
    InvalidConfirmationCodeError,
    InsufficientStockError,
    InvalidOrderStatusError,
    EmailNotConfirmedError,
    DependentEntityExistsError,
    PaymentGatewayError
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(categories.router)
app.include_router(reviews.router)
app.include_router(cart.router)
app.include_router(payments.router)

os.makedirs(settings.FILES_DIR, exist_ok=True)

app.mount(settings.IMAGES_BASE_PATH, StaticFiles(directory=settings.FILES_DIR), name="static")


def create_exception_handler(status_code, initial_detail):
    async def exception_handler(_: Request, exception: PetStoreApiError) -> JSONResponse:
        content = {"detail": initial_detail}
        if exception.message:
            content["detail"] = exception.message
        return JSONResponse(status_code=status_code, content=content, headers=exception.headers)

    return exception_handler


exception_handlers = [
    (ResourceDoesNotExistError, status.HTTP_404_NOT_FOUND, "Resource not found"),
    (ResourceAlreadyExistsError, status.HTTP_409_CONFLICT, "Resource already exists"),
    (NotEnoughRightsError, status.HTTP_403_FORBIDDEN, "Not enough rights to execute the operation"),
    (InvalidTokenError, status.HTTP_401_UNAUTHORIZED, "Invalid token"),
    (InvalidCredentialsError, status.HTTP_401_UNAUTHORIZED, "Invalid credentials"),
    (FileTooLargeError, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File is too large"),
    (NotSupportedFileTypeError, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "File type is not allowed"),
    (LimitExceededError, status.HTTP_409_CONFLICT, "Limit exceeded"),
    (InvalidConfirmationCodeError, status.HTTP_401_UNAUTHORIZED, "Invalid confirmation code"),
    (InsufficientStockError, status.HTTP_409_CONFLICT, "Out of stock"),
    (InvalidOrderStatusError, status.HTTP_409_CONFLICT, "Invalid order status"),
    (EmailNotConfirmedError, status.HTTP_403_FORBIDDEN, "Email not confirmed"),
    (DependentEntityExistsError, status.HTTP_409_CONFLICT, "Dependent entity exists"),
    (PaymentGatewayError, status.HTTP_500_INTERNAL_SERVER_ERROR, "Payment gateway error"),
]

for exc, code, message in exception_handlers:
    app.add_exception_handler(
        exc_class_or_status_code=exc,
        handler=create_exception_handler(code, message)
    )
