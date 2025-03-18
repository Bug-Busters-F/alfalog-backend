from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


# To customize SQLAlchemy ``db.Model``
class BaseModel(DeclarativeBase):
    # common fields between models
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now())
