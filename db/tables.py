from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy_service import Base


class Task(Base):
    __tablename__ = "tasks"

    id: M[int] = column(primary_key=True)
    user_id: M[int] = column(type_=BIGINT)
    message_id: M[int | None]

