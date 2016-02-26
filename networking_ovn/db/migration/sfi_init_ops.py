from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'sfis',
        sa.Column('tenant_id', sa.String(length=255), nullable=True),
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('firewall_id', sa.String(length=255), nullable=True),
        sa.Column('application_id', sa.String(length=255), nullable=True),
        sa.Column('in_port_id', sa.String(length=255), nullable=True),
        sa.Column('out_port_id', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'))
