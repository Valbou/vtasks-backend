from uuid import uuid4
from datetime import datetime
from pytz import utc
from typing import Optional
from dataclasses import dataclass

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from vtasks.users.validators import get_valid_email, PasswordChecker


@dataclass
class User:
    id: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    hash_password: str = ""
    locale: str = ""
    created_at: datetime = datetime.now(utc)
    last_login_at: Optional[datetime] = None

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        locale: str = "en_GB",
        hash_password: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_login_at: Optional[datetime] = None,
    ) -> None:
        self.id = id or uuid4().hex
        self.first_name = first_name
        self.last_name = last_name
        self.set_email(email.lower())
        if hash_password:
            self.hash_password = hash_password
        self.locale = locale
        self.created_at = created_at or datetime.now(utc)
        self.last_login_at = last_login_at

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_email(self, email: str) -> bool:
        self.email = get_valid_email(email) or ""
        return True

    def set_password(self, password: str):
        self._check_password_complexity(password)
        ph = PasswordHasher()
        self.hash_password = ph.hash(password)

    def check_password(self, password: str):
        ph = PasswordHasher()
        try:
            return ph.verify(self.hash_password, password)
        except VerifyMismatchError:
            return False

    def _check_password_complexity(self, password: str) -> bool:
        password_checker = PasswordChecker()
        password_checker.check_complexity(password)
        return True

    def update_last_login(self):
        self.last_login_at = datetime.now(utc)
        return self.last_login_at

    def from_external_data(self, user_dict: dict):
        self.first_name = user_dict.get("first_name", self.first_name)
        self.last_name = user_dict.get("last_name", self.last_name)
        self.set_email(user_dict.get("email", self.email))
        if user_dict.get("password"):
            self.set_password(user_dict.get("password", ""))

    def to_external_data(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created_at": str(self.created_at),
            "last_login_at": str(self.last_login_at),
        }

    def __str__(self) -> str:
        return self.full_name

    def __repr__(self):
        return f"<User {self.full_name!r}>"
