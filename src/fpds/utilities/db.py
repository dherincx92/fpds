import os
from datetime import datetime

from fpds.models import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

def insert_records(
    data,
    request_url: str,
    target_database_url_env_key: str = None
):
    from fpds.models.data import Fpds

    engine = create_engine(os.getenv(target_database_url_env_key))
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        rows = [
            Fpds(
                payload=record,
                operation="INSERT",
                request_url=request_url,
                created_at=datetime.now().isoformat()
            ) for record in data
        ]
        session.add_all(rows)
        session.commit()
