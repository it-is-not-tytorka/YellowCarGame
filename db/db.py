from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config_data.config import load_config, DatabaseConfig

db: DatabaseConfig = load_config().db


class Base(DeclarativeBase):
    pass


# there's a URL of your database. as default, you can use "sqlite:///project.db"
# also you can put your url using arguments of a db object like in an example below
# DB_URL = f"{db.database}://{db.db_user}:{db.db_password}@{db.db_host}:{db.db_port}/{db.db_name}"
DB_URL = "sqlite:///project.db"

engine = create_engine(DB_URL)

Session = sessionmaker(engine)
session = Session()

# create database only at the first time
if not database_exists(DB_URL):
    create_database(DB_URL)
