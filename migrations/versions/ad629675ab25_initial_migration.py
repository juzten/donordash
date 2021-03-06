"""initial migration

Revision ID: ad629675ab25
Revises:
Create Date: 2019-07-24 23:33:12.618625

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = 'ad629675ab25'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('donation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sqlalchemy_utils.types.arrow.ArrowType(), nullable=True),
    sa.Column('donor_id', sa.Unicode(), nullable=False),
    sa.Column('donor_name', sa.Unicode(), nullable=True),
    sa.Column('donor_email', sa.Unicode(), nullable=True),
    sa.Column('donor_gender', sa.Unicode(), nullable=True),
    sa.Column('donor_address', sa.Unicode(), nullable=True),
    sa.Column('donation_amount', sa.Numeric(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('donation_file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_on', sqlalchemy_utils.types.arrow.ArrowType(), nullable=True),
    sa.Column('filename', sa.Unicode(), nullable=False),
    sa.Column('uuid_filename', sa.Unicode(), nullable=False),
    sa.Column('processed', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('email', sa.Unicode(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('donation_file')
    op.drop_table('donation')
    # ### end Alembic commands ###
