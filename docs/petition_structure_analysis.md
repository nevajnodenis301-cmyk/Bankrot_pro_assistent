# BANKRUPTCY PETITION TEMPLATE - STRUCTURE ANALYSIS

Based on analysis of 5 court-accepted bankruptcy petitions.

## DOCUMENT STRUCTURE (Common Pattern)

All petitions follow this consistent structure:

### 1. HEADER SECTION
- Court name and address
- Blank lines for spacing
- Debtor (applicant) information
  * Full name
  * INN/SNILS
  * Full address
  * Contact phone

### 2. CREDITOR LIST
Multiple creditors, each with:
  * Sequential number
  * Organization name
  * OGRN/INN
  * Full address

### 3. TITLE
"ЗАЯВЛЕНИЕ
о признании гражданина несостоятельным (банкротом)"

### 4. DEBTOR PERSONAL DATA
- Full name, date of birth
- Passport details (series, number, issued by, date, code)
- Registration address
- INN/SNILS assignment

### 5. ENTREPRENEURIAL STATUS
- Confirmation of not being registered as IP
- Reference to confirmation document with number and date

### 6. TOTAL DEBT DECLARATION
"В настоящее время общий размер кредиторской задолженности составляет [AMOUNT] рублей [KOPECKS] копейки включает в себя:"

### 7. DETAILED DEBT BREAKDOWN
For each creditor:
- Sequential number matching creditor list
- Organization name
- One or more debt entries:
  * "согласно официальной выписки [SOURCE] составляет [AMOUNT] рублей [KOPECKS] копеек."
  * SOURCE: typically "СКОРИНГ БЮРО" or "ОКБ"

### 8. LOAN PURPOSE
"Кредитные обязательства являются потребительскими и не связаны с осуществлением предпринимательской деятельности. Денежные средства в кредит были взяты для потребительских нужд."

### 9. BANK ACCOUNTS
"Информация о счетах, открытых в банках и иных кредитных организациях приведена в форме «Опись имущества должника гражданина»."

### 10. ELECTRONIC MONEY
"Электронные денежные средства у [DEBTOR_SURNAME] [INITIALS] отсутствуют. Операции с такими денежными средствами за трехлетний период, предшествующий дате подачи заявления о признании банкротом, должник не совершал."

### 11. MARITAL STATUS
Two variants:
A) Married: "[DEBTOR] состоит в официальном браке с [SPOUSE_NAME], что подтверждается свидетельством о заключении брака [CERTIFICATE_NUMBER] от [DATE] года."
B) Divorced: "[DEBTOR] не состоит в официальном браке, что подтверждается свидетельством о расторжении брака [CERTIFICATE_NUMBER] от [DATE] года."

### 12. CHILDREN/DEPENDENTS
Two variants:
A) Has children: "У [DEBTOR] на иждивении есть несовершеннолетний ребенок / несовершеннолетние дети:"
   - Child name, date of birth, certificate details
B) No children: "У [DEBTOR] на иждивении нет несовершеннолетних детей."

### 13. EMPLOYMENT STATUS
Variants:
A) Unemployed: "[DEBTOR] официально не трудоустроен(а)."
B) Self-employed: "[DEBTOR] официально не трудоустроен, [DEBTOR] является самозанятым."
   - Income details by year with reference numbers

### 14. REAL ESTATE
"За [DEBTOR] не зарегистрировано недвижимое имущество."

### 15. MOVABLE PROPERTY
Variants:
A) None: "Движимое имущество у [DEBTOR] не имеется."
B) Has property: "Движимое имущество у [DEBTOR] имеется, а именно [DESCRIPTION]"

### 16. SECURITIES
"Акции, а также иные ценные бумаги у [DEBTOR] отсутствуют, участником каких-либо коммерческих организаций он/она не является."

### 17. ACCOUNTS RECEIVABLE
"Дебиторская задолженность у [DEBTOR] отсутствует."

### 18. TRANSACTION HISTORY (3 years)
"Информация о сделках, совершенных [DEBTOR] в течение трех лет, до даты подачи в суд настоящего заявления с:"
A) Real estate: Usually "Сделки не совершались;"
B) Securities: Usually "Сделки не совершались;"
C) LLC shares: Usually "Сделки не совершались;"
D) Vehicles: Either "Сделки не совершались;" or detailed transaction info

### 19. LEGAL GROUNDS
Extensive citations of Federal Law 127-FZ articles:
- Article 6, paragraph 2 (debt threshold)
- Article 4, paragraph 2 (debt calculation)
- Article 213.3 (right to file)
- Article 213.4 (obligation to file)
- Article 213.6 (insolvency definition)
- References to Supreme Court Plenum decisions

### 20. FINANCIAL ANALYSIS APPOINTMENT
"Прошу назначить финансового управляющего из числа членов саморегулируемой организации [SRO_NAME]"

### 21. PETITION REQUESTS
Numbered list:
1. Recognize debtor as bankrupt
2. Introduce debt restructuring procedure (with duration)
3. Appoint financial manager
4. Include creditors in register
5. Publish information in EFRSB
6. Award financial manager fee

### 22. APPENDICES
Detailed list of attached documents (varies by case)

### 23. SIGNATURE BLOCK
Date and signature line

## KEY VARIABLE FIELDS IDENTIFIED

### Court Information
- court_name
- court_address

### Debtor Personal
- debtor_full_name
- debtor_surname
- debtor_name_patronymic
- debtor_initials
- debtor_birth_date
- debtor_passport_series
- debtor_passport_number
- debtor_passport_issued_by
- debtor_passport_date
- debtor_passport_code
- debtor_address_full
- debtor_inn
- debtor_snils
- debtor_phone
- debtor_gender (for proper conjugation)

### IP Status
- ip_certificate_number
- ip_certificate_date

### Creditors (array)
- creditor_number
- creditor_name
- creditor_ogrn
- creditor_inn
- creditor_address

### Debts (array, linked to creditors)
- debt_creditor_number
- debt_amount_rubles
- debt_amount_kopecks
- debt_source (ОКБ or СКОРИНГ БЮРО)

### Total Debt
- total_debt_rubles
- total_debt_kopecks
- total_debt_words

### Family Status
- is_married (boolean)
- spouse_name
- marriage_certificate_number
- marriage_certificate_date
- divorce_certificate_number (if divorced)
- divorce_certificate_date (if divorced)

### Children (array)
- has_children (boolean)
- child_name
- child_birth_date
- child_certificate_number
- child_certificate_date
- child_passport_details (if over 14)

### Employment
- is_employed (boolean)
- is_self_employed (boolean)
- income_by_year (array if self-employed)

### Property
- real_estate_exists (boolean)
- real_estate_description
- movable_property_exists (boolean)
- movable_property_description
- has_pledged_property (boolean)
- pledged_property_description

### Transactions
- transactions_real_estate
- transactions_securities
- transactions_llc_shares
- transactions_vehicles

### Financial Manager
- sro_name
- restructuring_duration

### Appendices (array)
- appendix_number
- appendix_description
- appendix_pages

### Signature
- petition_date
