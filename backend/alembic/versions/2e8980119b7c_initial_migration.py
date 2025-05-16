"""Initial migration

Revision ID: 2e8980119b7c
Revises: 0073ee243905
Create Date: 2025-05-16 15:48:26.637592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e8980119b7c'
down_revision: Union[str, None] = '0073ee243905'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
