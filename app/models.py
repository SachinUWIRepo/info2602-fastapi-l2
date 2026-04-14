from typing import Optional

from pwdlib import PasswordHash
from sqlmodel import Field, SQLModel

password_hash = PasswordHash.recommended()


class User(SQLModel, table=True):
    """Represents a user record in the database."""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    password: str

    def __init__(self, username, email, password):
        """Create a user and hash the provided password."""
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        """Hash and store a user's password."""
        self.password = password_hash.hash(password)

    def __str__(self) -> str:
        """Return a readable string version of the user."""
        return f"(User id={self.id}, username={self.username} ,email={self.email})"
