"""verification_dry_run

Revision ID: 5c4dae6973d4
Revises: 8b4c5ba04ef7
Create Date: 2026-03-20 14:14:14.062862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5c4dae6973d4'
down_revision: Union[str, Sequence[str], None] = '8b4c5ba04ef7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Fix the typo in motif_stats by renaming instead of dropping
    op.alter_column('motif_stats', 'occurence_count', 
                    new_column_name='occurrence_count', 
                    type_=sa.Integer(),
                    server_default='0',
                    nullable=False)

    # 2. Correct nullability drift for artist_genre_map
    op.alter_column('artist_genre_map', 'affinity_score',
               existing_type=sa.Float(),
               nullable=True,
               existing_server_default=sa.text("'1'"))

    # 3. Correct nullability drift for track_scale_map
    op.alter_column('track_scale_map', 'is_default',
               existing_type=sa.Boolean(),
               nullable=True,
               existing_server_default=sa.text("'0'"))

def downgrade() -> None:
    # Revert changes for rollback integrity
    op.alter_column('track_scale_map', 'is_default',
               existing_type=sa.Boolean(),
               nullable=False,
               existing_server_default=sa.text("'0'"))

    op.alter_column('artist_genre_map', 'affinity_score',
               existing_type=sa.Float(),
               nullable=False,
               existing_server_default=sa.text("'1'"))

    op.alter_column('motif_stats', 'occurrence_count', 
                    new_column_name='occurence_count', 
                    type_=sa.Integer(),
                    server_default='0',
                    nullable=False)
