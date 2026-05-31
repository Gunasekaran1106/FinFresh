"""
Custom exception hierarchy for the Finance Tracker API.

Using typed exceptions instead of bare ValueError/RuntimeError lets the
route layer catch exactly what it expects and map each type to a precise
HTTP status code — no string parsing required.
"""


class AppError(Exception):
    """Base class for all application-level errors."""
    default_message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# Auth errors
# ---------------------------------------------------------------------------

class DuplicateEmailError(AppError):
    """Raised when registration is attempted with an already-registered email."""
    default_message = "An account with this email already exists."


class InvalidCredentialsError(AppError):
    """Raised when email/password combination does not match any account."""
    default_message = "Invalid email or password."


class UserNotFoundError(AppError):
    """Raised when a user lookup by ID returns nothing."""
    default_message = "User not found."


# ---------------------------------------------------------------------------
# Token errors
# ---------------------------------------------------------------------------

class TokenExpiredError(AppError):
    """Raised when a JWT has passed its expiry time."""
    default_message = "Token has expired. Please log in again."


class TokenInvalidError(AppError):
    """Raised when a JWT is malformed, tampered with, or wrong type."""
    default_message = "Invalid token. Authentication failed."


# ---------------------------------------------------------------------------
# Transaction errors
# ---------------------------------------------------------------------------

class TransactionNotFoundError(AppError):
    """Raised when a transaction does not exist or belongs to another user."""
    default_message = "Transaction not found."


class InvalidObjectIdError(AppError):
    """Raised when a string cannot be parsed as a BSON ObjectId."""
    default_message = "The provided ID is not valid."


# ---------------------------------------------------------------------------
# Database errors
# ---------------------------------------------------------------------------

class DatabaseError(AppError):
    """Raised when a MongoDB operation fails unexpectedly."""
    default_message = "A database error occurred. Please try again."