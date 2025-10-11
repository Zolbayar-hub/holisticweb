"""Add num_people column to bookings

Revision ID: add_num_people_to_bookings
Revises: 
Create Date: 2025-10-11 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_num_people_to_bookings'
down_revision = None
depends_on = None


def upgrade():
    # Add num_people column to booking table with default value of 1
    op.add_column('booking', sa.Column('num_people', sa.Integer(), nullable=False, server_default='1'))


def downgrade():
    # Remove num_people column from booking table
    op.drop_column('booking', 'num_people')
