class ServiceError(Exception):
    def __init__(self, message=None, status_code=None):

        self.message = message or getattr(self, 'message', 'Internal server error')
        self.status_code = status_code or getattr(self, 'status_code', 500)
        
        super().__init__(self.message)

class Unauthorized(ServiceError):
    message = "Unauthorized"
    status_code = 401

class ExpiredToken(Unauthorized):
    message = "Token expired, you need to log in again."

class InvalidCredentials(ServiceError):
    message = "Invalid credentials."
    status_code = 400

class InvalidToken(Unauthorized):
    message = "Invalid token."

class EmailAlreadyInUse(ServiceError):
    message = "Email already in use"
    status_code = 409

class Forbidden(ServiceError):
    message = "Forbidden"
    status_code = 403

class TaskNotFound(ServiceError):
    message = "Task not found"
    status_code = 404

class TitleEmpty(ServiceError):
    message = "Title cannot be empty"
    status_code = 400

class UserNotFound(ServiceError):
    message = "User does not exist"
    status_code = 404