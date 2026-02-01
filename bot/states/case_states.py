from aiogram.fsm.state import State, StatesGroup


class CaseCreation(StatesGroup):
    waiting_full_name = State()
    waiting_total_debt = State()
    waiting_procedure_type = State()  # Property Realization or Debt Restructuring
    waiting_creditor_name = State()
    waiting_creditor_debt = State()
    add_more_creditors = State()
    confirmation = State()


class DocumentGeneration(StatesGroup):
    """FSM states for document generation flow"""
    select_document_type = State()  # Select which document to generate
    select_case = State()  # Select case for document generation
    confirm_generation = State()  # Confirm before generating


class ClientDataEdit(StatesGroup):
    """Editing client personal data"""
    menu = State()

    # Passport editing
    edit_passport_series = State()
    edit_passport_number = State()
    edit_passport_issued_by = State()
    edit_passport_date = State()
    edit_passport_code = State()

    # Personal info
    edit_birth_date = State()
    edit_address = State()
    edit_phone = State()
    edit_inn = State()
    edit_snils = State()
    edit_gender = State()


class CreditorManagement(StatesGroup):
    """Managing creditors for a case"""
    menu = State()

    # Adding new creditor
    add_name = State()
    add_ogrn = State()
    add_inn = State()
    add_address = State()
    add_debt_amount = State()

    # Editing creditor
    edit_select = State()
    edit_name = State()
    edit_ogrn = State()
    edit_inn = State()
    edit_address = State()
    edit_debt_amount = State()

    # Deleting creditor
    delete_select = State()
    delete_confirm = State()


class DebtManagement(StatesGroup):
    """Managing detailed debts for a case"""
    menu = State()

    # Adding new debt
    add_creditor_select = State()  # Select which creditor this debt is for
    add_amount_rubles = State()
    add_amount_kopecks = State()
    add_source = State()  # e.g., "ОКБ", "договор №123"

    # Editing debt
    edit_select = State()
    edit_creditor = State()
    edit_amount_rubles = State()
    edit_amount_kopecks = State()
    edit_source = State()

    # Deleting debt
    delete_select = State()
    delete_confirm = State()


# ==================== GROUP 1: FAMILY & EMPLOYMENT ====================

class FamilyDataEdit(StatesGroup):
    """Managing family information"""
    menu = State()

    # Marital status
    edit_marital_status = State()
    edit_spouse_name = State()
    edit_marriage_cert_number = State()
    edit_marriage_cert_date = State()
    edit_divorce_cert_number = State()
    edit_divorce_cert_date = State()

    # Children - adding
    add_child_name = State()
    add_child_birth_date = State()
    add_child_document_type = State()  # Choose: passport or birth_certificate

    # Birth certificate path
    add_child_cert_number = State()
    add_child_cert_date = State()

    # Passport path (for children 14+)
    add_child_passport_series = State()
    add_child_passport_number = State()
    add_child_passport_issued_by = State()
    add_child_passport_date = State()
    add_child_passport_code = State()

    # Delete
    delete_child_select = State()
    delete_child_confirm = State()


class EmploymentDataEdit(StatesGroup):
    """Managing employment and income data"""
    menu = State()

    # Employment status
    edit_employment_status = State()
    edit_employer_name = State()

    # Self-employed income records
    add_income_year = State()
    add_income_rubles = State()
    add_income_kopecks = State()
    add_income_cert_number = State()

    # Delete income
    delete_income_select = State()
    delete_income_confirm = State()


# ==================== GROUP 2: PROPERTY & TRANSACTIONS ====================

class PropertyManagement(StatesGroup):
    """Managing property and assets"""
    menu = State()

    # Real estate toggle
    confirm_real_estate_toggle = State()

    # Adding vehicle
    add_vehicle_make = State()
    add_vehicle_model = State()
    add_vehicle_year = State()
    add_vehicle_vin = State()
    add_vehicle_color = State()
    add_vehicle_pledged = State()  # Yes/No
    add_pledge_creditor = State()
    add_pledge_document = State()

    # Delete
    delete_property_select = State()
    delete_property_confirm = State()


class TransactionManagement(StatesGroup):
    """Managing 3-year transaction history"""
    menu = State()

    # Adding transaction
    add_transaction_type = State()  # real_estate/securities/llc_shares/vehicles
    add_transaction_description = State()
    add_transaction_date = State()
    add_transaction_amount = State()

    # Delete
    delete_transaction_select = State()
    delete_transaction_confirm = State()


# ==================== GROUP 3: COURT & SRO ====================

class CourtInfoEdit(StatesGroup):
    """Managing court and SRO information"""
    menu = State()
    edit_court_name = State()
    edit_court_address = State()
    edit_sro_name = State()
    edit_restructuring_duration = State()
    edit_insolvency_grounds = State()
