"""fix

Revision ID: 80d865a77468
Revises: ad629675ab25
Create Date: 2019-07-24 23:36:53.819622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80d865a77468'
down_revision = 'ad629675ab25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('donation_file', sa.Column('donation_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_donation_file_donation_id'), 'donation_file', ['donation_id'], unique=False)
    op.create_foreign_key(None, 'donation_file', 'donation', ['donation_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'donation_file', type_='foreignkey')
    op.drop_index(op.f('ix_donation_file_donation_id'), table_name='donation_file')
    op.drop_column('donation_file', 'donation_id')
    # ### end Alembic commands ###
