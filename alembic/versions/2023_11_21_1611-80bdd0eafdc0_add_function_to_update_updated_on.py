"""Add function to update updated_at.

Revision ID: 80bdd0eafdc0
Revises:
Create Date: 2023-11-21 16:11:13.365305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '80bdd0eafdc0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS update_updated_at")
