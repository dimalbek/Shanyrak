"""comments create

Revision ID: 51ee922b61c1
Revises: 1115ca39228c
Create Date: 2024-04-19 01:06:09.419419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51ee922b61c1'
down_revision = '1115ca39228c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###
