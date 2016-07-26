from urllib.parse import urlsplit

from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import (
    BIGINT,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship

from miracle.models.base import Model


class URL(Model):
    __tablename__ = 'url'

    __table_args__ = (
        Index('url_hostname_idx', 'hostname'),
        Index('url_scheme_idx', 'scheme'),
    )

    id = Column(BIGINT(), autoincrement=True, primary_key=True)
    full = Column(String(2048), nullable=False, unique=True)
    hostname = Column(String(256))
    scheme = Column(String(8))

    sessions = relationship(
        'Session', back_populates='url', lazy='dynamic',
        cascade='all, delete-orphan', passive_deletes=True)

    @classmethod
    def from_url(cls, url):
        result = urlsplit(url)
        return cls(
            full=url,
            scheme=result.scheme,
            hostname=result.hostname)


class User(Model):
    __tablename__ = 'user'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    token = Column(String(36), nullable=False, unique=True)

    sessions = relationship(
        'Session', back_populates='user', lazy='dynamic',
        cascade='all, delete-orphan', passive_deletes=True)


class Session(Model):
    __tablename__ = 'session'

    __table_args__ = (
        Index('session_user_id_start_time_idx', 'user_id', 'start_time'),
    )

    id = Column(BIGINT(), autoincrement=True, primary_key=True)

    url_id = Column(BIGINT(), ForeignKey('url.id', ondelete='CASCADE'))
    user_id = Column(Integer(), ForeignKey('user.id', ondelete='CASCADE'))
    start_time = Column(TIMESTAMP(), nullable=False)

    duration = Column(Integer())

    url = relationship('URL', back_populates='sessions')
    user = relationship('User', back_populates='sessions')
