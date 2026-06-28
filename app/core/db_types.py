"""Tipos de columna compatibles con PostgreSQL y SQLite.

SQLite no soporta ARRAY nativo. Este módulo provee un TypeDecorator
que almacena arrays como JSON string en SQLite y como ARRAY nativo
en PostgreSQL, permitiendo tests con SQLite en memoria.
"""

import json
from typing import Any

from sqlalchemy import String, Text, Integer
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from sqlalchemy.types import TypeDecorator


class CompatibleArray(TypeDecorator):
    """Array compatible con PostgreSQL (ARRAY nativo) y SQLite (JSON).

    En PostgreSQL: usa ARRAY(<item_type>) nativo.
    En SQLite: serializa/deserializa como JSON string en columna Text.

    Uso:
        CompatibleArray(String)   -> array de strings
        CompatibleArray(Integer)  -> array de enteros
    """

    impl = Text
    cache_ok = True

    def __init__(self, item_type=None):
        super().__init__()
        self._item_type = item_type or String

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(self._item_type()))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return list(value)
        return json.dumps(list(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if dialect.name == "postgresql":
            return list(value) if value else []
        if isinstance(value, str):
            return json.loads(value)
        return list(value) if value else []
