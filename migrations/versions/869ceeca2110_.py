"""empty message

Revision ID: 869ceeca2110
Revises: 74d6f349ce33
Create Date: 2020-05-29 13:46:40.414782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '869ceeca2110'
down_revision = '74d6f349ce33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name_test', sa.String(length=64), nullable=True))
    op.create_index(op.f('ix_users_name_test'), 'users', ['name_test'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_name_test'), table_name='users')
    op.drop_column('users', 'name_test')
    # ### end Alembic commands ###
