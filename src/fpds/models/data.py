from sqlalchemy import JSON, TIMESTAMP, VARCHAR, Column, Integer, String

from fpds.models import Base


class Fpds(Base):
    __tablename__ = "fpds"

    id = Column(Integer, primary_key=True)
    payload = Column(JSON, nullable=False)
    operation = Column(String(500))
    request_url = Column(VARCHAR)
    created_at = Column(TIMESTAMP(timezone=True))
