"""empty message

Revision ID: 6320509f588b
Revises: 7f9ba727f350
Create Date: 2020-01-11 21:57:45.341581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6320509f588b'
down_revision = '7f9ba727f350'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'genres')
    op.drop_column('venues', 'genres')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('genres', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('artists', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
