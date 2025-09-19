"""Add embedding_id to Tenant model

Revision ID: 9061a471e583
Revises: 9bdec2f4ddce
Create Date: 2025-05-20 16:49:49.942575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9061a471e583'
down_revision: Union[str, None] = '9bdec2f4ddce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
