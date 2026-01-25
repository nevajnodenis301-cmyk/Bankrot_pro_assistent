from aiogram.fsm.state import State, StatesGroup


class CaseCreation(StatesGroup):
    waiting_full_name = State()
    waiting_total_debt = State()
    waiting_creditor_name = State()
    waiting_creditor_debt = State()
    add_more_creditors = State()
    confirmation = State()


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
