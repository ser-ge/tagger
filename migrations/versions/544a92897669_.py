"""empty message

Revision ID: 544a92897669
Revises: b65f13b0ab29
Create Date: 2020-06-07 16:33:54.603493

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '544a92897669'
down_revision = 'b65f13b0ab29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('evernote_token', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'evernote_token')
    # ### end Alembic commands ###
