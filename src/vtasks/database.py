import os
from enum import Enum
from typing import Optional, Union, Literal

from sqlalchemy import create_engine, Engine
from .base import Base


class DBType(Enum):
    TEST = "test"
    PROD = "prod"


class SQLService:
    def __init__(
        self,
        database: Optional[DBType] = None,
        echo: Union[None, bool, Literal["debug"]] = False,
    ) -> None:
        self.echo: Union[None, bool, Literal["debug"]] = echo
        self.database: Optional[DBType] = database

    def get_database_url(self) -> str:
        DB_TYPE = os.getenv("DB_TYPE")
        BD_DRIVER = os.getenv("BD_DRIVER")
        DB_USER = os.getenv("DB_USER")
        DB_PASS = os.getenv("DB_PASS")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = (
            os.getenv("DB_NAME")
            if self.database == DBType.PROD
            else os.getenv("DB_TEST")
        )

        return (
            f"{DB_TYPE}+{BD_DRIVER}://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

    def get_engine(self) -> Engine:
        return create_engine(self.get_database_url(), echo=self.echo)

    def create_tables(self):
        Base.metadata.create_all(bind=self.get_engine())

    def drop_tables(self):
        Base.metadata.drop_all(bind=self.get_engine())
