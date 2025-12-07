from sqlalchemy.orm import DeclarativeBase

from app.models.mixins import TimestampMixin


class Base(DeclarativeBase, TimestampMixin):
    pass
