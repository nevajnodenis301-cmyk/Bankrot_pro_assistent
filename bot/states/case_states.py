from aiogram.fsm.state import State, StatesGroup


class CaseCreation(StatesGroup):
    waiting_full_name = State()
    waiting_total_debt = State()
    waiting_creditor_name = State()
    waiting_creditor_debt = State()
    add_more_creditors = State()
    confirmation = State()
