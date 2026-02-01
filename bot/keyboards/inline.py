from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Yes/No inline keyboard with navigation"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data="yes"),
                InlineKeyboardButton(text="❌ Нет, завершить", callback_data="no"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="back_creditor"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_case"),
            ]
        ]
    )
    return keyboard


def get_cases_keyboard(cases: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard with list of cases"""
    buttons = []
    for case in cases[:10]:  # Limit to 10 cases
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{case['case_number']} - {case['full_name'][:20]}",
                    callback_data=f"case_{case['id']}",
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_case_keyboard(case_id: int) -> InlineKeyboardMarkup:
    """Keyboard for case actions"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Получить документ", callback_data=f"doc_{case_id}")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_list")],
        ]
    )
    return keyboard


def get_procedure_type_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting procedure type during case creation"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🏠 Реализация имущества",
                callback_data="procedure:Property Realization"
            )],
            [InlineKeyboardButton(
                text="📊 Реструктуризация долгов",
                callback_data="procedure:Debt Restructuring"
            )],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="procedure:back"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="procedure:cancel"),
            ],
        ]
    )
    return keyboard


def get_document_types_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for selecting document type to generate"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="📜 Заявление о банкротстве",
                callback_data="doctype:bankruptcy_petition"
            )],
            [InlineKeyboardButton(
                text="📋 Простое заявление",
                callback_data="doctype:bankruptcy_application"
            )],
            [InlineKeyboardButton(
                text="📨 Уведомление кредиторов",
                callback_data="doctype:creditor_notification"
            )],
            [InlineKeyboardButton(
                text="⚖️ Ходатайство в суд",
                callback_data="doctype:court_motion"
            )],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="doctype:cancel")],
        ]
    )
    return keyboard


def get_cases_for_document_keyboard(cases: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard with list of cases for document generation"""
    buttons = []
    for case in cases[:10]:  # Limit to 10 cases
        procedure = case.get('procedure_type', '')
        procedure_emoji = "🏠" if procedure == "Property Realization" else "📊" if procedure == "Debt Restructuring" else "📁"
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{procedure_emoji} {case['case_number']} - {case['full_name'][:20]}",
                    callback_data=f"doccase_{case['id']}",
                )
            ]
        )
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="doccase_back"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="doccase_cancel"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_case_documents_keyboard(case_id: int, documents: list[dict]) -> InlineKeyboardMarkup:
    """Keyboard for viewing/downloading case documents"""
    buttons = []
    for doc in documents[:8]:  # Limit to 8 documents
        doc_name = doc.get('file_name', 'document')
        # Shorten the filename for display
        display_name = doc_name[:30] + "..." if len(doc_name) > 30 else doc_name
        buttons.append([
            InlineKeyboardButton(
                text=f"📥 {display_name}",
                callback_data=f"download:{case_id}:{doc_name[:50]}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_case_docs")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
