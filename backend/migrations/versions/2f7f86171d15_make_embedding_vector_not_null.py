"""make embedding_vector not null

Revision ID: 2f7f86171d15
Revises: f188f29c58d8
Create Date: 2026-01-21 22:25:09.005622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f7f86171d15'
down_revision: Union[str, Sequence[str], None] = 'f188f29c58d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'chunk_embeddings',
        'embedding_vector',
        nullable=False
    )
    


def downgrade() -> None:
    """Downgrade schema."""
    pass
