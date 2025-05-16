"""Initial migration

Revision ID: 399be29daedb
Revises: 6996dc3b0130
Create Date: 2025-05-16 15:42:25.539649

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '399be29daedb'
down_revision: Union[str, None] = '6996dc3b0130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
