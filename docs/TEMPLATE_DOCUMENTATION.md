# BANKRUPTCY PETITION TEMPLATE - COMPLETE DOCUMENTATION

## Template File
`bankruptcy_petition_template_v1_jinja2.docx`

## Template Engine
This template uses **Mustache/Handlebars** syntax with double curly braces: `{{variable_name}}`

For Python rendering, use **Jinja2** or **python-docx-template** library.

---

## COMPLETE VARIABLE REFERENCE

### 1. COURT INFORMATION

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{court_name}}` | String | "Арбитражный суд Краснодарского края" | Full court name |
| `{{court_address}}` | String | "350063, г. Краснодар. Ул. Постовая 32" | Complete court address |

---

### 2. DEBTOR PERSONAL INFORMATION

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{debtor_full_name}}` | String | "Иванов Иван Иванович" | Full name (Surname Name Patronymic) |
| `{{debtor_surname}}` | String | "Иванов" | Surname only |
| `{{debtor_name_patronymic}}` | String | "Иван Иванович" | Name and patronymic |
| `{{debtor_initials}}` | String | "И.И." | Initials |
| `{{debtor_birth_date}}` | String | "01.01.1980" | Date of birth |
| `{{debtor_inn}}` | String | "123456789012" | INN (12 digits) |
| `{{debtor_snils}}` | String | "123-456-789 01" | SNILS with hyphens |
| `{{debtor_address}}` | String | "350053, Краснодарский край, г. Краснодар, ул. Средняя, д.81/2, кв.34" | Full registration address |
| `{{debtor_phone}}` | String | "8-962-024-10-31" | Contact phone |
| `{{debtor_gender_pronoun}}` | String | "он" or "она" | Gender pronoun for conjugation |

### Passport Information

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{debtor_passport_series}}` | String | "03 23" | Passport series |
| `{{debtor_passport_number}}` | String | "494963" | Passport number |
| `{{debtor_passport_issued_by}}` | String | "ГУ МВД России по Краснодарскому краю" | Issuing authority |
| `{{debtor_passport_date}}` | String | "23.03.2023" | Issue date |
| `{{debtor_passport_code}}` | String | "230-004" | Department code |

---

### 3. INDIVIDUAL ENTREPRENEUR STATUS

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{ip_certificate_number}}` | String | "ИЭС9965-25-22931174" | Certificate number |
| `{{ip_certificate_date}}` | String | "24.06.2025" | Certificate date |

---

### 4. CREDITORS (Array/List)

Use loop: `{{#creditors}} ... {{/creditors}}`

**For each creditor:**

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{number}}` | Integer | 1, 2, 3... | Sequential creditor number |
| `{{name}}` | String | "ПАО \"Сбербанк России\"" | Creditor organization name |
| `{{ogrn}}` | String | "1027700132195" | OGRN |
| `{{inn}}` | String | "7707083893" | INN |
| `{{address}}` | String | "117312, город Москва, ул. Вавилова, д.19" | Full address |

**Example data structure:**
```python
creditors = [
    {
        "number": 1,
        "name": "ПАО \"Сбербанк России\"",
        "ogrn": "1027700132195",
        "inn": "7707083893",
        "address": "117312, город Москва, ул. Вавилова, д.19"
    },
    {
        "number": 2,
        "name": "АО \"Альфа-Банк\"",
        "ogrn": "1027700067328",
        "inn": "7728168971",
        "address": "107078, город Москва, Каланчевская ул., д.27"
    }
]
```

---

### 5. TOTAL DEBT

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{total_debt_rubles}}` | String | "2 067 915" | Total debt in rubles (formatted with spaces) |
| `{{total_debt_rubles_word}}` | String | "рублей" | Word "рублей/рубля/рубль" (proper declension) |
| `{{total_debt_kopecks}}` | String | "42" | Kopecks |
| `{{total_debt_kopecks_word}}` | String | "копейки" | Word "копейки/копеек/копейка" |

---

### 6. DEBT BREAKDOWN (Array/List)

Use loop: `{{#debts}} ... {{/debts}}`

**For each debt entry:**

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{number}}` | Integer | 1, 2, 3... | Debt entry number (matches creditor) |
| `{{creditor_name}}` | String | "ПАО \"Сбербанк России\"" | Creditor name |
| `{{amount_rubles}}` | String | "167 420" | Amount in rubles |
| `{{amount_rubles_word}}` | String | "рублей" | Declension |
| `{{amount_kopecks}}` | String | "68" | Kopecks |
| `{{amount_kopecks_word}}` | String | "копеек" | Declension |
| `{{source}}` | String | "СКОРИНГ БЮРО" or "ОКБ" | Data source |

**Example:**
```python
debts = [
    {
        "number": 1,
        "creditor_name": "ПАО \"Сбербанк России\"",
        "amount_rubles": "167 420",
        "amount_rubles_word": "рублей",
        "amount_kopecks": "68",
        "amount_kopecks_word": "копеек",
        "source": "СКОРИНГ БЮРО"
    },
    {
        "number": 2,
        "creditor_name": "АО \"Альфа-Банк\"",
        "amount_rubles": "1 500 000",
        "amount_rubles_word": "рублей",
        "amount_kopecks": "00",
        "amount_kopecks_word": "копеек",
        "source": "ОКБ"
    }
]
```

---

### 7. MARITAL STATUS

**Option A: Married**
```
{{#is_married}} ... {{/is_married}}
```

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{spouse_name}}` | String | "Иванова Мария Петровна" | Spouse full name |
| `{{marriage_certificate_number}}` | String | "I-АЗ № 580976" | Certificate number |
| `{{marriage_certificate_date}}` | String | "19.10.2019" | Marriage date |

**Option B: Divorced**
```
{{#is_divorced}} ... {{/is_divorced}}
```

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{divorce_certificate_number}}` | String | "IV-АГ № 578340" | Certificate number |
| `{{divorce_certificate_date}}` | String | "01.06.2024" | Divorce date |

---

### 8. CHILDREN/DEPENDENTS

**If has children:**
```
{{#has_children}} ... {{/has_children}}
```

**Multiple children flag:**
```
{{#multiple_children}} ... {{/multiple_children}}
```

**Children array:**
```
{{#children}} ... {{/children}}
```

**For each child:**

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{child_name}}` | String | "Иванов Артур Иванович" | Child full name |
| `{{child_birth_date}}` | String | "30.01.2021" | Birth date |

**If child under 14 (has birth certificate):**
```
{{#child_has_certificate}} ... {{/child_has_certificate}}
```

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{child_certificate_number}}` | String | "I-АЗ №671938" | Birth certificate number |
| `{{child_certificate_date}}` | String | "4.02.2021" | Issue date |

**If child 14+ (has passport):**
```
{{#child_has_passport}} ... {{/child_has_passport}}
```

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{child_passport_series}}` | String | "03 25" | Passport series |
| `{{child_passport_number}}` | String | "166684" | Passport number |
| `{{child_passport_issued_by}}` | String | "ГУ МВД РОССИИ по Краснодарскому краю" | Issuer |
| `{{child_passport_date}}` | String | "06.03.2025" | Issue date |
| `{{child_passport_code}}` | String | "230-005" | Department code |

**Example:**
```python
children = [
    {
        "child_name": "Иванов Артур Иванович",
        "child_birth_date": "30.01.2021",
        "child_has_certificate": True,
        "child_certificate_number": "I-АЗ №671938",
        "child_certificate_date": "4.02.2021",
        "child_has_passport": False
    }
]
```

---

### 9. EMPLOYMENT & INCOME

**Employment flags:**

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{is_employed}}` | Boolean | True/False | Officially employed |
| `{{is_self_employed}}` | Boolean | True/False | Self-employed status |

**If self-employed, income by year:**
```
{{#income_years}} ... {{/income_years}}
```

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{year}}` | String | "2024" | Tax year |
| `{{amount}}` | String | "1 199 628 рублей 40 копеек" | Annual income |
| `{{amount_word}}` | String | "рублей" | Declension |
| `{{certificate_number}}` | String | "93949637" | Certificate reference |

**Example:**
```python
income_years = [
    {
        "year": "2023",
        "amount": "90 000 рублей 00 копеек",
        "amount_word": "рублей",
        "certificate_number": "93949502"
    },
    {
        "year": "2024",
        "amount": "1 199 628 рублей 40 копеек",
        "amount_word": "рублей",
        "certificate_number": "93949637"
    }
]
```

---

### 10. REAL ESTATE

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{has_real_estate}}` | Boolean | True/False | Has registered property |
| `{{real_estate_description}}` | String | "квартира по адресу..." | Property description (if any) |

---

### 11. MOVABLE PROPERTY

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{has_movable_property}}` | Boolean | True/False | Has movable property |
| `{{movable_property_description}}` | String | "легковой автомобиль JAC JS6 2024 года выпуска, серого цвета, VIN: LJ166A259R4711110" | Property details |
| `{{property_type}}` | String | "автомобиль" | Property type name |

**If pledged:**
```
{{#is_pledged}} ... {{/is_pledged}}
```

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{pledge_creditor}}` | String | "АО \"ТБанк\"" | Pledge holder |
| `{{pledge_document}}` | String | "Актом №КБ-0423.42 от 21.11.2025 года" | Proof document |

---

### 12. TRANSACTION HISTORY (3 years)

**For each transaction type:**

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{transactions_real_estate}}` | String/Boolean | "Сделки не совершались;" or details | Real estate transactions |
| `{{transactions_securities}}` | String/Boolean | "Сделки не совершались;" or details | Securities transactions |
| `{{transactions_llc_shares}}` | String/Boolean | "Сделки не совершались;" or details | LLC shares transactions |
| `{{transactions_vehicles}}` | String/Boolean | "Была совершена сделка..." or "Сделки не совершались;" | Vehicle transactions |

**Example vehicle transaction:**
```python
transactions_vehicles = "Была совершена сделка о купли-продажи транспортного средства Toyota Voltz 2002 года. Серого цвета, цена сделки 10 000 рублей 00 копеек, о чем свидетельствует ДКП от 26.08.2024 года. Данные денежные средства были направлены на погашение платежей по кредитным обязательствам."
```

---

### 13. INSOLVENCY GROUNDS

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{insolvency_grounds}}` | String | "гражданин прекратил расчеты с кредиторами..." | Specific insolvency reasons |

---

### 14. FINANCIAL MANAGER

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{sro_name}}` | String | "Ассоциация «Урало-Сибирское объединение арбитражных управляющих»" | SRO organization name |
| `{{restructuring_duration}}` | String | "3 месяца" or "6 месяцев" | Restructuring period |

---

### 15. CREDITOR REGISTRY (for petition requests)

Use loop: `{{#creditor_registry}} ... {{/creditor_registry}}`

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{number}}` | Integer | 1, 2, 3... | Registry number |
| `{{name}}` | String | "ПАО \"Сбербанк России\"" | Creditor name |
| `{{amount}}` | String | "167 420" | Amount in rubles |
| `{{kopecks}}` | String | "68" | Kopecks |

---

### 16. APPENDICES

Use loop: `{{#appendices}} ... {{/appendices}}`

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{number}}` | Integer | 1, 2, 3... | Appendix number |
| `{{description}}` | String | "Копия паспорта гражданина РФ" | Document description |
| `{{pages}}` | Integer | 2 | Number of pages |

**Example:**
```python
appendices = [
    {"number": 1, "description": "Копия паспорта гражданина РФ", "pages": 2},
    {"number": 2, "description": "Копия СНИЛС", "pages": 1},
    {"number": 3, "description": "Справка о неучастии в качестве ИП", "pages": 1},
    {"number": 4, "description": "Выписка СКОРИНГ БЮРО", "pages": 15}
]
```

---

### 17. SIGNATURE

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `{{petition_date}}` | String | "25.01.2026" | Petition filing date |

---

## RENDERING THE TEMPLATE

### Option 1: Using python-docx-template

```python
from docxtpl import DocxTemplate

# Load template
doc = DocxTemplate("bankruptcy_petition_template_v1_jinja2.docx")

# Prepare data
context = {
    "court_name": "Арбитражный суд Краснодарского края",
    "court_address": "350063, г. Краснодар. Ул. Постовая 32",
    "debtor_full_name": "Иванов Иван Иванович",
    "debtor_surname": "Иванов",
    "debtor_initials": "И.И.",
    # ... all other fields
    "creditors": [
        {
            "number": 1,
            "name": "ПАО \"Сбербанк России\"",
            "ogrn": "1027700132195",
            "inn": "7707083893",
            "address": "117312, город Москва, ул. Вавилова, д.19"
        }
    ],
    "debts": [...],
    "is_married": True,
    "spouse_name": "Иванова Мария Петровна",
    # etc.
}

# Render
doc.render(context)

# Save
doc.save("filled_petition.docx")
```

### Option 2: Using Jinja2 (for text-based approach)

First extract text from template, then use Jinja2, then recreate DOCX.

---

## HELPER FUNCTIONS

### Number to Russian Words (for amounts)

```python
def rubles_declension(number):
    """Return proper declension: рубль/рубля/рублей"""
    if number % 10 == 1 and number % 100 != 11:
        return "рубль"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return "рубля"
    else:
        return "рублей"

def kopecks_declension(number):
    """Return proper declension: копейка/копейки/копеек"""
    if number % 10 == 1 and number % 100 != 11:
        return "копейка"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return "копейки"
    else:
        return "копеек"
```

### Format Amount

```python
def format_amount(rubles, kopecks):
    """Format amount with spaces: 1234567.89 -> '1 234 567 рублей 89 копеек'"""
    rubles_formatted = f"{rubles:,}".replace(',', ' ')
    rubles_word = rubles_declension(rubles)
    kopecks_word = kopecks_declension(kopecks)
    return {
        "amount_rubles": rubles_formatted,
        "amount_rubles_word": rubles_word,
        "amount_kopecks": f"{kopecks:02d}",
        "amount_kopecks_word": kopecks_word
    }
```

---

## CONDITIONAL SECTIONS

The template uses Mustache/Handlebars conditional syntax:

**If statement (show if true):**
```
{{#variable}}
  Content shown when variable is true/exists
{{/variable}}
```

**Unless statement (show if false):**
```
{{^variable}}
  Content shown when variable is false/doesn't exist
{{/variable}}
```

**Example:**
```
{{#has_children}}
У должника есть дети
{{/has_children}}
{{^has_children}}
У должника нет детей
{{/has_children}}
```

---

## VALIDATION CHECKLIST

Before rendering, ensure:

- [ ] All creditors have matching debt entries
- [ ] Total debt equals sum of all debts
- [ ] Passport data is complete
- [ ] Marital status is properly set (married XOR divorced)
- [ ] Children array is empty if has_children = False
- [ ] Employment flags match income data
- [ ] Appendices list is complete
- [ ] All dates are in DD.MM.YYYY format
- [ ] All amounts use Russian number declensions

---

## NEXT STEPS

1. Create data collection form/UI
2. Implement validation logic
3. Set up rendering pipeline
4. Test with real data
5. Add PDF export capability
