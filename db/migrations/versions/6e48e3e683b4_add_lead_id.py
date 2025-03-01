"""add lead_id

Revision ID: 6e48e3e683b4
Revises: d0fe3d0a8589
Create Date: 2025-03-01 21:59:13.931425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e48e3e683b4'
down_revision = 'd0fe3d0a8589'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('crm_last_lead_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'crm_last_lead_id')
    # ### end Alembic commands ###
