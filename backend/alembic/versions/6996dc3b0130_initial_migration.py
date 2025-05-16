"""Initial migration

Revision ID: 6996dc3b0130
Revises: 2cc728fd6907
Create Date: 2025-05-16 15:32:22.744902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6996dc3b0130'
down_revision: Union[str, None] = '2cc728fd6907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
