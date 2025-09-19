"""first migrations

Revision ID: 1178c83c1f63
Revises: 9061a471e583
Create Date: 2025-05-20 16:51:19.471366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1178c83c1f63'
down_revision: Union[str, None] = '9061a471e583'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
