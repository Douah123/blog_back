"""add parent comment id to comments

Revision ID: 1f7c9f2a8b11
Revises: c97960ed565d
Create Date: 2026-03-26 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f7c9f2a8b11'
down_revision = 'c97960ed565d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_comment_id', sa.Integer(), nullable=True))
        batch_op.create_index(batch_op.f('ix_comments_parent_comment_id'), ['parent_comment_id'], unique=False)
        batch_op.create_foreign_key(
            'fk_comments_parent_comment_id_comments',
            'comments',
            ['parent_comment_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('fk_comments_parent_comment_id_comments', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_comments_parent_comment_id'))
        batch_op.drop_column('parent_comment_id')
