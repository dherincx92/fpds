from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

# https://docs.sqlalchemy.org/en/14/core/metadata.html#sqlalchemy.schema.MetaData.params.naming_convention
naming_convention = {
    "ix": "idx_%(column_0_N_label)s",
    "uq": "%(table_name)s_%(column_0_N_name)s_uq",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

# figure out a way to set default schema regardless of SQL engine
metadata = MetaData(schema="public", naming_convention=naming_convention)
mapper_registry = registry(metadata=metadata)

Base: Any = mapper_registry.generate_base()
