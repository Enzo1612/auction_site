from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import DateTime
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'db79be77c74e'
down_revision = '6ab1286f2f11'
branch_labels = None
depends_on = None

def upgrade():
    # Rename the column
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.alter_column('buy_date', new_column_name='end_time', existing_type=sa.DateTime, nullable=False)

    # Set a default value for existing rows
    auctions_table = table(
        'auctions',
        column('end_time', DateTime)
    )
    op.execute(
        auctions_table.update().values(
            end_time=datetime.utcnow()  # Set a default value for existing rows
        )
    )

def downgrade():
    # Rename the column back to buy_date
    with op.batch_alter_table('auctions', schema=None) as batch_op:
        batch_op.alter_column('end_time', new_column_name='buy_date', existing_type=sa.DateTime, nullable=False)