"""empty message

Revision ID: 6210895f4869
Revises: 7c22f79a5358
Create Date: 2020-06-12 11:53:16.995843

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6210895f4869'
down_revision = '7c22f79a5358'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tag', sa.Column('user_id', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'tag', ['tag_id'])
    op.create_foreign_key(None, 'tag', 'user', ['user_id'], ['user_id'])
    op.create_unique_constraint(None, 'user', ['user_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'tag', type_='foreignkey')
    op.drop_constraint(None, 'tag', type_='unique')
    op.drop_column('tag', 'user_id')
    # ### end Alembic commands ###