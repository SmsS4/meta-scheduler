import uuid

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Double
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UUID
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class OptResult(Base):
    __tablename__ = "quiz"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    create_time = Column(String, nullable=False)
    version = Column(String, nullable=False)
    sharpe_ratio = Column(postgresql.ARRAY(Double))
    trades = Column(postgresql.ARRAY(Integer))
    result = Column(postgresql.ARRAY(Double))
    profit = Column(postgresql.ARRAY(Double))
    profit_factor = Column(postgresql.ARRAY(Double))
    recovery_factor = Column(postgresql.ARRAY(Double))
    expected_payoff = Column(postgresql.ARRAY(Double))
    drawdown = Column(postgresql.ARRAY(Double))
    custom = Column(postgresql.ARRAY(Double))
    inptrailingstop = Column(postgresql.ARRAY(Double))
