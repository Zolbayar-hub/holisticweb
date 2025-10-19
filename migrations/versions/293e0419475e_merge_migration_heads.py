"""Merge migration heads

Revision ID: 293e0419475e
Revises: add_language_to_services, add_num_people_to_bookings
Create Date: 2025-10-18 12:24:18.796166

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '293e0419475e'
down_revision = ('add_language_to_services', 'add_num_people_to_bookings')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
