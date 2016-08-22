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
    __tablename__ = 'urls'

    __table_args__ = (
        Index('urls_hostname_idx', 'hostname'),
        Index('urls_scheme_idx', 'scheme'),
    )

    id = Column(BIGINT(), autoincrement=True, primary_key=True)
    url = Column(String(2048), nullable=False, unique=True)
    hostname = Column(String(256))
    scheme = Column(String(8))

    sessions = relationship(
        'Session', back_populates='url', lazy='dynamic',
        cascade='all, delete-orphan', passive_deletes=True)

    @staticmethod
    def from_url(url):
        result = urlsplit(url)
        return {
            'url': url,
            'scheme': result.scheme,
            'hostname': result.hostname,
        }


class User(Model):
    __tablename__ = 'users'

    id = Column(Integer(), autoincrement=True, primary_key=True)
    token = Column(String(36), nullable=False, unique=True)
    created = Column(TIMESTAMP())

    sessions = relationship(
        'Session', back_populates='user', lazy='dynamic',
        cascade='all, delete-orphan', passive_deletes=True)


class Session(Model):
    __tablename__ = 'sessions'

    __table_args__ = (
        Index('sessions_url_id_idx', 'url_id'),
        Index('sessions_user_id_idx', 'user_id'),
    )

    id = Column(BIGINT(), autoincrement=True, primary_key=True)

    url_id = Column(BIGINT(), ForeignKey('urls.id', ondelete='CASCADE'))
    user_id = Column(Integer(), ForeignKey('users.id', ondelete='CASCADE'))
    start_time = Column(TIMESTAMP(), nullable=False)

    duration = Column(Integer())

    url = relationship('URL', back_populates='sessions')
    user = relationship('User', back_populates='sessions')
