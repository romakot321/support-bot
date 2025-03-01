from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy_service import Base


class User(Base):
    __tablename__ = "users"

    id: M[int] = column(primary_key=True)
    telegram_id: M[int] = column(type_=BIGINT)
    crm_id: M[int | None]
    crm_last_lead_id: M[int | None]

