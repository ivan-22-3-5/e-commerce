# TODO: consider renaming of the exceptions in this module

class PetStoreApiError(Exception):
    def __init__(self, message: str = "Service is not available", headers=None):
        self.message = message
        self.headers = headers
        super().__init__(self.message)


class ResourceDoesNotExistError(PetStoreApiError):
    pass


class ResourceAlreadyExistsError(PetStoreApiError):
    pass


class NotEnoughRightsError(PetStoreApiError):
    pass


class InvalidTokenError(PetStoreApiError):
    pass


class InvalidCredentialsError(PetStoreApiError):
    pass


class InvalidConfirmationCodeError(PetStoreApiError):
    pass


class InvalidPayloadError(PetStoreApiError):
    pass


class InvalidSignatureError(PetStoreApiError):
    pass


class FileTooLargeError(PetStoreApiError):
    pass


class NotSupportedFileTypeError(PetStoreApiError):
    pass


class LimitExceededError(PetStoreApiError):
    pass


class InsufficientStockError(PetStoreApiError):
    pass


class InvalidOrderStatusError(PetStoreApiError):
    pass


class EmailNotConfirmedError(PetStoreApiError):
    pass
