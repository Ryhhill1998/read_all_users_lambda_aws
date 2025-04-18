from dataclasses import dataclass


@dataclass
class Settings:
    db_host: str
    db_name: str
    db_user: str
    db_pass: str
    queue_url: str


@dataclass
class User:
    id: str
    refresh_token: str
