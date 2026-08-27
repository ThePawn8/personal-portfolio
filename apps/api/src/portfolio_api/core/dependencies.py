"""FastAPI dependencies.

Resources live on `app.state` and are reached through these, so nothing imports a global
singleton and every dependency can be overridden in a test.
"""

from typing import Annotated

from fastapi import Depends, Request

from portfolio_api.core.config import Settings
from portfolio_api.core.database import Database


def get_settings_dep(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def get_database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


SettingsDep = Annotated[Settings, Depends(get_settings_dep)]
DatabaseDep = Annotated[Database, Depends(get_database)]
