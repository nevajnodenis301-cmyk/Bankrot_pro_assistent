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
