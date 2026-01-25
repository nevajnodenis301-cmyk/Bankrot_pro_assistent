# Bankrot PRO - Complete Redesign Plan

## Goal
Integrate the comprehensive bankruptcy petition template with step-by-step data collection.

## Database Changes Needed

### New Models/Tables:
1. **Children** - child dependents (name, birth_date, passport/certificate info)
2. **Income** - yearly income records for self-employed
3. **Property** - real estate and movable property
4. **Transactions** - 3-year transaction history
5. **Debts** - detailed debt breakdown (separate from Creditor)

### Expand Existing Models:
- **Case**: Add spouse_name, marriage_certificate, employment fields, etc.
- **Creditor**: Add OGRN, address, contact info

## Bot Menu Structure

### Main Menu:
1. 📋 Мои дела
2. ➕ Новое дело
3. 📄 Создать документ
4. 💬 AI-помощник

### Case Detail Menu (when viewing a case):
1. 👤 Данные клиента
2. 💰 Кредиторы
3. 📊 Задолженность
4. 👨‍👩‍👧 Семья
5. 💼 Занятость
6. 🏠 Имущество
7. 📝 Сделки (3 года)
8. 📄 Создать заявление

### Each Section has Sub-menu:
- View current data
- Add new
- Edit existing
- Delete

## Implementation Steps

### Phase 1: Database (Priority)
- Create migration file
- Add new models
- Update existing models
- Test migration

### Phase 2: API Updates
- Update schemas
- Create CRUD operations for new models
- Update document_service.py

### Phase 3: Bot Redesign
- Create new FSM states
- Build step-by-step handlers
- Create inline keyboards
- Add validation

### Phase 4: Document Generation
- Map all fields to template
- Add helper functions (declensions, formatting)
- Test generation

## Timeline
- Phase 1: ~2 hours
- Phase 2: ~3 hours
- Phase 3: ~4 hours
- Phase 4: ~2 hours

Total: ~11 hours of development
