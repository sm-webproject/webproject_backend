"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from env import DB_SCHEMA

${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades.replace(f"schema='{schema}'", 'schema=DB_SCHEMA').replace(f"op.create_index(op.f('ix_{schema}_", "op.create_index(op.f('ix_' + DB_SCHEMA + '_").replace(f", ['{schema}.", ", [DB_SCHEMA + '.") if upgrades else "pass"}


def downgrade():
    ${downgrades.replace(f"schema='{schema}'", 'schema=DB_SCHEMA').replace(f"op.drop_index(op.f('ix_{schema}_", "op.drop_index(op.f('ix_' + DB_SCHEMA + '_").replace(f", ['{schema}.", ", [DB_SCHEMA + '.") if downgrades else "pass"}
