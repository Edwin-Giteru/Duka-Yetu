"""Initial migration

Revision ID: 0073ee243905
Revises: 399be29daedb
Create Date: 2025-05-16 15:43:25.518841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0073ee243905'
down_revision: Union[str, None] = '399be29daedb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
