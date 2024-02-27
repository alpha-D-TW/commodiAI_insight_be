"""Add knowledge table.

Revision ID: f06b5c59fd81
Revises: 80bdd0eafdc0
Create Date: 2023-11-21 16:16:03.470120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f06b5c59fd81'
down_revision: Union[str, None] = '80bdd0eafdc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('knowledge',
                    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
                    sa.Column('s3_key', sa.String(length=200), nullable=False),
                    sa.Column('file_name', sa.String(length=200), nullable=False),
                    sa.Column('embedding_ids', sa.String(), nullable=True),
                    sa.Column('type', sa.Enum('MARKET_DATA', 'DOMAIN_KNOWLEDGE', name='knowledgetype'), nullable=False),
                    sa.Column('status', sa.Enum('CREATED', 'OS_LOAD_QUEUED', 'OS_LOAD_SUCCEED', 'OS_LOAD_FAILED',
                                                'CSV_LOAD_QUEUED', 'CSV_LOAD_SUCCEED', 'CSV_LOAD_FAILED',
                                                name='knowledgestatus'), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )
    op.execute(
        """
        CREATE TRIGGER update_knowledge_updated_at
            BEFORE UPDATE
            ON
                knowledge
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at();
        """
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('knowledge')
    sa.Enum(name="knowledgetype").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="knowledgestatus").drop(op.get_bind(), checkfirst=False)
    # ### end Alembic commands ###