from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from babel import Locale
from pytz import utc

from vtasks.base.config import LOCALE, TIMEZONE
from vtasks.secutity.utils import check_password, get_id, hash_from_password
from vtasks.secutity.validators import PasswordChecker, get_valid_email


@dataclass
class User:
    id: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    hash_password: str = ""
    locale: Locale = ""
    timezone: str = ""
    created_at: datetime = datetime.now(utc)
    last_login_at: Optional[datetime] = None

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        locale: Optional[Locale] = None,
        timezone: Optional[str] = None,
        hash_password: Optional[str] = None,
        id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_login_at: Optional[datetime] = None,
    ) -> None:
        self.id = id or get_id()
        self.first_name = first_name
        self.last_name = last_name
        self.set_email(email.lower())
        if hash_password:
            self.hash_password = hash_password
        self.locale = locale or Locale.parse(LOCALE)
        self.timezone = timezone or TIMEZONE
        self.created_at = created_at or datetime.now(utc)
        self.last_login_at = last_login_at

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def set_email(self, email: str) -> bool:
        self.email = get_valid_email(email) or ""
        return True

    def set_password(self, password: str) -> bool:
        self._check_password_complexity(password)
        self.hash_password = hash_from_password(password)
        return True

    def check_password(self, password: str) -> bool:
        return check_password(self.hash_password, password)

    def _check_password_complexity(self, password: str) -> bool:
        password_checker = PasswordChecker()
        password_checker.check_complexity(password)
        return True

    def update_last_login(self) -> datetime:
        self.last_login_at = datetime.now(utc)
        return self.last_login_at

    def from_external_data(self, user_dict: dict):
        self.first_name = user_dict.get("first_name", self.first_name)
        self.last_name = user_dict.get("last_name", self.last_name)
        self.locale = Locale.parse(user_dict.get("locale")) or self.locale
        self.timezone = user_dict.get("timezone", self.timezone)

    def to_external_data(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat()
            if self.last_login_at
            else None,
            "locale": str(self.locale),
            "timezone": self.timezone,
        }

    def __str__(self) -> str:
        return self.full_name

    def __repr__(self):
        return f"<User {self.full_name!r}>"
