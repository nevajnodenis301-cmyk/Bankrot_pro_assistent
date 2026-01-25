"""add_comprehensive_template_fields

Revision ID: f73eea63f712
Revises: 003
Create Date: 2026-01-25 14:43:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f73eea63f712'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to cases table
    op.add_column('cases', sa.Column('ip_certificate_number', sa.String(length=100), nullable=True))
    op.add_column('cases', sa.Column('ip_certificate_date', sa.Date(), nullable=True))
    op.add_column('cases', sa.Column('spouse_name', sa.String(length=255), nullable=True))
    op.add_column('cases', sa.Column('marriage_certificate_number', sa.String(length=100), nullable=True))
    op.add_column('cases', sa.Column('marriage_certificate_date', sa.Date(), nullable=True))
    op.add_column('cases', sa.Column('divorce_certificate_number', sa.String(length=100), nullable=True))
    op.add_column('cases', sa.Column('divorce_certificate_date', sa.Date(), nullable=True))
    op.add_column('cases', sa.Column('is_employed', sa.Boolean(), nullable=True, default=False))
    op.add_column('cases', sa.Column('is_self_employed', sa.Boolean(), nullable=True, default=False))
    op.add_column('cases', sa.Column('employer_name', sa.String(length=255), nullable=True))
    op.add_column('cases', sa.Column('has_real_estate', sa.Boolean(), nullable=True, default=False))
    op.add_column('cases', sa.Column('has_movable_property', sa.Boolean(), nullable=True, default=False))
    op.add_column('cases', sa.Column('restructuring_duration', sa.String(length=50), nullable=True))
    op.add_column('cases', sa.Column('insolvency_grounds', sa.Text(), nullable=True))
    
    # Add new columns to creditors table
    op.add_column('creditors', sa.Column('number', sa.Integer(), nullable=True))
    op.add_column('creditors', sa.Column('ogrn', sa.String(length=20), nullable=True))
    op.add_column('creditors', sa.Column('inn', sa.String(length=12), nullable=True))
    op.add_column('creditors', sa.Column('address', sa.Text(), nullable=True))
    
    # Create debts table
    op.create_table(
        'debts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('creditor_id', sa.Integer(), nullable=True),
        sa.Column('number', sa.Integer(), nullable=True),
        sa.Column('creditor_name', sa.String(length=255), nullable=False),
        sa.Column('amount_rubles', sa.Integer(), nullable=False),
        sa.Column('amount_kopecks', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creditor_id'], ['creditors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create children table
    op.create_table(
        'children',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('child_name', sa.String(length=255), nullable=False),
        sa.Column('child_birth_date', sa.Date(), nullable=False),
        sa.Column('child_has_certificate', sa.Boolean(), nullable=False, default=True),
        sa.Column('child_certificate_number', sa.String(length=100), nullable=True),
        sa.Column('child_certificate_date', sa.Date(), nullable=True),
        sa.Column('child_has_passport', sa.Boolean(), nullable=False, default=False),
        sa.Column('child_passport_series', sa.String(length=4), nullable=True),
        sa.Column('child_passport_number', sa.String(length=6), nullable=True),
        sa.Column('child_passport_issued_by', sa.Text(), nullable=True),
        sa.Column('child_passport_date', sa.Date(), nullable=True),
        sa.Column('child_passport_code', sa.String(length=10), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create income table
    op.create_table(
        'income',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.String(length=4), nullable=False),
        sa.Column('amount_rubles', sa.Integer(), nullable=False),
        sa.Column('amount_kopecks', sa.Integer(), nullable=False),
        sa.Column('certificate_number', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create properties table
    op.create_table(
        'properties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('property_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('vehicle_make', sa.String(length=100), nullable=True),
        sa.Column('vehicle_model', sa.String(length=100), nullable=True),
        sa.Column('vehicle_year', sa.Integer(), nullable=True),
        sa.Column('vehicle_vin', sa.String(length=50), nullable=True),
        sa.Column('vehicle_color', sa.String(length=50), nullable=True),
        sa.Column('is_pledged', sa.Boolean(), nullable=False, default=False),
        sa.Column('pledge_creditor', sa.String(length=255), nullable=True),
        sa.Column('pledge_document', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['case_id'], ['cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop new tables
    op.drop_table('transactions')
    op.drop_table('properties')
    op.drop_table('income')
    op.drop_table('children')
    op.drop_table('debts')
    
    # Remove columns from creditors
    op.drop_column('creditors', 'address')
    op.drop_column('creditors', 'inn')
    op.drop_column('creditors', 'ogrn')
    op.drop_column('creditors', 'number')
    
    # Remove columns from cases
    op.drop_column('cases', 'insolvency_grounds')
    op.drop_column('cases', 'restructuring_duration')
    op.drop_column('cases', 'has_movable_property')
    op.drop_column('cases', 'has_real_estate')
    op.drop_column('cases', 'employer_name')
    op.drop_column('cases', 'is_self_employed')
    op.drop_column('cases', 'is_employed')
    op.drop_column('cases', 'divorce_certificate_date')
    op.drop_column('cases', 'divorce_certificate_number')
    op.drop_column('cases', 'marriage_certificate_date')
    op.drop_column('cases', 'marriage_certificate_number')
    op.drop_column('cases', 'spouse_name')
    op.drop_column('cases', 'ip_certificate_date')
    op.drop_column('cases', 'ip_certificate_number')
