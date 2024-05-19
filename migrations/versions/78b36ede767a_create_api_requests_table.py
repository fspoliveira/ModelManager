"""create api_requests table

Revision ID: 78b36ede767a
Revises: 
Create Date: 2024-05-19 03:41:59.693

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '78b36ede767a'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Verificar se a tabela já existe
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'api_requests' not in inspector.get_table_names():
        op.create_table(
            'api_requests',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('request_type', sa.String(50), nullable=False),
            sa.Column('request_json', sa.JSON, nullable=False),
            sa.Column('response_json', sa.JSON, nullable=False),
            sa.Column('created_at', sa.DateTime, default=sa.func.current_timestamp())
        )

def downgrade():
    op.drop_table('api_requests')