from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    db_name: str


@dataclass
class TgBot:
    token: str


@dataclass
class OpenAI:
    openai_key: str


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    open_ai: OpenAI


def load_config(path: str | None = None):
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(token=env("BOT_TOKEN")),
        db=DatabaseConfig(
            database=env("DATABASE"),
            db_user=env("DB_USER"),
            db_password=env("DB_PASSWORD"),
            db_host=env("DB_HOST"),
            db_port=env("DB_PORT"),
            db_name=env("DB_NAME"),
        ),
        open_ai=OpenAI(openai_key=env("OPENAI_KEY")),
    )
