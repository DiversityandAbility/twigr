import os
from typing import List
from datetime import datetime, timezone

import databases
import sqlalchemy
from sqlalchemy.dialects.postgresql import JSONB

database = databases.Database(
    os.environ["DATABASE_URL"], force_rollback="TESTING" in os.environ
)
metadata = sqlalchemy.MetaData()


twigs = sqlalchemy.Table(
    "twigs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column(
        "project", sqlalchemy.String(length=64), nullable=True, index=True
    ),
    sqlalchemy.Column(
        "added_on",
        sqlalchemy.TIMESTAMP(timezone=True),
        nullable=False,
        index=True,
    ),
    sqlalchemy.Column("data", JSONB, nullable=False),
    sqlalchemy.Index("idx_data", "data", postgresql_using="gin"),
)


async def find_twigs(
    filters: List[sqlalchemy.sql.elements.ColumnElement] = tuple(),
):
    query = twigs.select()
    for exp in filters:
        query = query.where(exp)
    query = query.order_by(twigs.c.added_on.desc())
    return await database.fetch_all(query=query)


async def create_twig(twig):
    twig["added_on"] = datetime.now(tz=timezone.utc)
    query = twigs.insert()
    await database.execute(query=query, values=twig)
