"""fix2

Revision ID: 714d7af61c94
Revises: 80d865a77468
Create Date: 2019-07-24 23:38:45.731234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '714d7af61c94'
down_revision = '80d865a77468'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('donation', sa.Column('donation_file_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_donation_donation_file_id'), 'donation', ['donation_file_id'], unique=False)
    op.create_foreign_key(None, 'donation', 'donation_file', ['donation_file_id'], ['id'])
    op.drop_index('ix_donation_file_donation_id', table_name='donation_file')
    op.drop_constraint('donation_file_donation_id_fkey', 'donation_file', type_='foreignkey')
    op.drop_column('donation_file', 'donation_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('donation_file', sa.Column('donation_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('donation_file_donation_id_fkey', 'donation_file', 'donation', ['donation_id'], ['id'])
    op.create_index('ix_donation_file_donation_id', 'donation_file', ['donation_id'], unique=False)
    op.drop_constraint(None, 'donation', type_='foreignkey')
    op.drop_index(op.f('ix_donation_donation_file_id'), table_name='donation')
    op.drop_column('donation', 'donation_file_id')
    # ### end Alembic commands ###
