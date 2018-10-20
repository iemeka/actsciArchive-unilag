"""it worked. first time

Revision ID: 9470daaf8b89
Revises: 1bd9d8879cf0
Create Date: 2018-10-20 09:08:48.436379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9470daaf8b89'
down_revision = '1bd9d8879cf0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('course_details', 'year',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=8),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('course_details', 'year',
               existing_type=sa.String(length=8),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
