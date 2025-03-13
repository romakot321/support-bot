from sqlalchemy import BIGINT
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy_service import Base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import UniqueConstraint


UniqueConstraint.argument_for("postgresql", 'nulls_not_distinct', None)


@compiles(UniqueConstraint, "postgresql")
def compile_create_uc(create, compiler, **kw):
    """Add NULLS NOT DISTINCT if its in args."""
    stmt = compiler.visit_unique_constraint(create, **kw)
    postgresql_opts = create.dialect_options["postgresql"]

    if postgresql_opts.get("nulls_not_distinct"):
        return stmt.rstrip().replace("UNIQUE (", "UNIQUE NULLS NOT DISTINCT (")
    return stmt


class User(Base):
    __tablename__ = "users"

    id: M[int] = column(primary_key=True)
    telegram_id: M[int] = column(type_=BIGINT)
    crm_id: M[int | None]
    crm_last_lead_id: M[int | None]
    current_chat_id: M[str | None]
    current_chat_ref_id: M[str | None]

    __table_args__ = (
        UniqueConstraint(
            "current_chat_id",
            postgresql_nulls_not_distinct=True,  # here it is.
            name="uix_currentchatid"
        ),
    )

