"""Allow multiple reviewed allocations per case; idempotency owns replay prevention."""

from alembic import op

revision = "003_partial"
down_revision = "fe37ee547197"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "allocations_org_id_investigation_id_invoice_id_key", "allocations", type_="unique"
    )


def downgrade():
    raise RuntimeError("Financial history cannot safely be collapsed; restore a compatible backup")
