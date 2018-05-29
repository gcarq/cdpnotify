import logging
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, create_engine, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker

logger = logging.getLogger(__name__)

_DECL_BASE = declarative_base()


def init(filename: str) -> None:
    """ Initialize persistence module """
    engine = create_engine(filename)
    session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=True))
    CDPEntity.session = session()
    CDPEntity.query = session.query_property()
    _DECL_BASE.metadata.create_all(engine)


class CDPEntity(_DECL_BASE):
    __tablename__ = 'cdps'

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, nullable=False)
    telegram_chat_id = Column(Integer, nullable=False)
    cdp_id = Column(Integer, nullable=False)
    notification_ratio = Column(Float, nullable=False)
    created = Column(DateTime, nullable=False, default=datetime.utcnow)
