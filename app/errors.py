class ServiceError(Exception):
    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self):
        super().__init__(self.message)

class InvalidCredentials(ServiceError):
    message = "Invalid credentials"
    status_code = 400

class ExpiredToken(ServiceError):
    message = "Token expired, login again"
    status_code = 401

class InvalidToken(ServiceError):
    message = "Unauthorized"
    status_code = 401

class EmailAlreadyInUse(ServiceError):
    message = "Email already in use"
    status_code = 409

