import hashlib
import hmac
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone

ITERATION = 100_000
PATTERN_EMAIL = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class User:
    def __init__(self, username: str, email: str, role: str) -> None:
        self.username = username
        self.email = email
        self.role = role
        self.active = True
        self.__password_hash = None
        self.__password_salt = None

    def set_password(self, password: str) -> None:
        self.__password_salt = os.urandom(16)
        password_bytes = password.encode("utf-8")
        self.__password_hash = hashlib.pbkdf2_hmac(
            "sha256", password_bytes, self.__password_salt, ITERATION
        )

    def check_password(self, password: str) -> bool:
        if self.__password_hash is None or self.__password_salt is None:
            return False

        password_bytes = password.encode("utf-8")
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256", password_bytes, self.__password_salt, ITERATION
        )

        return hmac.compare_digest(self.__password_hash, computed_hash)

    def deactivate(self) -> None:
        self.active = False

    def __str__(self) -> str:
        return (
            f"User(username={self.username!r}, email={self.email!r}, "
            f"role={self.role!r}, active={self.active!r})"
        )

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email_value: str) -> None:
        if not PATTERN_EMAIL.match(email_value):
            raise ValueError(f"Invalid email format: {email_value}")
        self._email = email_value


class Admin(User):
    def __init__(self, username, email, role, permissions=None):
        super().__init__(username, email, role)
        self.permissions = set(permissions) if permissions else set()

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        base_information = super().__str__()
        return f"{base_information}, permissions={self.permissions}"


class Session:
    def __init__(self, ip: str):
        self.ip = ip
        now = datetime.now(timezone.utc)
        self.login_time = now
        self.last_activity = now

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int) -> bool:
        if timeout_sec <= 0:
            raise ValueError("timeout_sec must be positive")

        # timedelta створюється автоматично
        downtime = datetime.now(timezone.utc) - self.last_activity
        return downtime.total_seconds() < timeout_sec


@dataclass
class LogEntry:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"

    def __init__(self):
        self.entries = []

    def add_log(self, username: str, action: str) -> None:
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            username=username, action=action)
        self.entries.append(entry)

    def show_all(self) -> None:
        if not self.entries:
            print("Журнал порожній")
            return
        for entry in self.entries:
            print(
                f"[{entry.timestamp:%Y-%m-%d %H:%M:%S}] "
                f"{entry.username}: {entry.action}"
            )


class UserAccount:
    SESSION_TIMEOUT_SEC = 900

    def __init__(self, user: User, session: Session = None,
                 audit_log: AuditLog = None):
        self.user = user
        self.session = session
        self.audit_log = audit_log if audit_log is not None else AuditLog()

    def login(self, username: str, password: str, ip: str) -> None:
        if (
            self.user.active
            and username == self.user.username
            and self.user.check_password(password)
        ):
            self.session = Session(ip)
            self.session.touch()
            self.audit_log.add_log(username, AuditLog.LOGIN_SUCCESS)
        else:
            self.audit_log.add_log(username, AuditLog.LOGIN_FAILURE)

    def is_authenticated(self) -> bool:
        if self.session is None:
            return False
        return self.session.is_active(self.SESSION_TIMEOUT_SEC)

    def logout(self) -> None:
        if self.session is not None:
            self.audit_log.add_log(self.user.username, AuditLog.LOGOUT)
            self.session = None

    def __getitem__(self, key: str):
        allowed_keys = {"user", "session", "audit_log"}

        if key not in allowed_keys:
            raise KeyError(f"Невідомий ключ: {key}")

        return getattr(self, key)

    def __setitem__(self, key: str, value) -> None:
        allowed_keys = {"user", "session", "audit_log"}

        if key not in allowed_keys:
            raise KeyError(f"Невідомий ключ: {key}")

        keyword_dictionary = {"user": User,
                              "session": Session, "audit_log": AuditLog}

        if not isinstance(value, keyword_dictionary[key]):
            raise TypeError(
                f"Для ключа {key} очікується тип {keyword_dictionary[key].__name__}"
            )

        setattr(self, key, value)
