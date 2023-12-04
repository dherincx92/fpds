import os
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fpds.models import Base


def insert(data, request_url: str, target_database_url_env_key: str) -> None:
    """Inserts FPDS records into a target database.

    Parameters
    ----------
    data:
        JSONified response from `fpdsRequest`
    request_url: `str`
        The request URL made to the FPDS ATOM feed.
    target_database_url_env_key: `str`
        Database URL environment key to insert data into.
    """
    from fpds.models.data import Fpds

    engine = create_engine(os.getenv(target_database_url_env_key))
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        rows = [
            Fpds(
                payload=record,
                operation="INSERT",
                request_url=request_url,
                created_at=datetime.now().isoformat(),
            )
            for record in data
        ]
        session.add_all(rows)
        session.commit()
