# BankrotPro  Система ведения дел о банкротстве

##  О проекте

Комплексная система для арбитражных управляющих и юристов по ведению дел о банкротстве физических лиц. Включает Telegram-бота для сбора данных, веб-интерфейс (Streamlit) для управления делами, и AI-ассистента для генерации документов.

##  Технологии

| Компонент | Стек |
|-----------|------|
| **API** | Python 3.11+, FastAPI, SQLAlchemy, Alembic |
| **Bot** | Python, aiogram 3.x, FSM |
| **Web** | Python, Streamlit |
| **Database** | PostgreSQL |
| **AI** | OpenAI API (GPT для документов) |
| **Deploy** | Docker, Docker Compose |

##  Структура проекта
```
bankrot_pro/
 api/                    # FastAPI бэкенд
    models/            # SQLAlchemy модели
    routers/           # API эндпоинты
    schemas/           # Pydantic схемы
    services/          # Бизнес-логика
    templates/         # Шаблоны документов (.docx)
    main.py           # Точка входа API
    database.py       # Подключение к БД
 bot/                   # Telegram бот
    handlers/         # Обработчики команд
    keyboards/        # Клавиатуры бота
    states/           # FSM состояния
    main.py          # Точка входа бота
 web/                   # Streamlit веб-интерфейс
    pages/            # Страницы приложения
    app.py           # Главная страница
 alembic/              # Миграции БД
 tests/                # Тесты
 docker-compose.yml    # Docker конфигурация
```

##  Команды
```bash
# Запуск
docker-compose up -d              # Запустить все
docker-compose up -d --build      # Пересобрать
docker-compose logs -f api        # Логи API
docker-compose logs -f bot        # Логи бота

# Миграции
docker-compose exec api alembic upgrade head
docker-compose exec api alembic revision -m "description"

# Тесты
pytest tests/ -v
```

##  ВАЖНО

- **НИКОГДА** не коммить .env файлы
- **ВСЕГДА** делать бэкап БД перед миграциями
- API защищён токеном  Authorization: Bearer {API_TOKEN}

##  Что НЕ делать

- Не изменять таблицы напрямую  только через Alembic
- Не удалять файлы в api/templates/
- Не менять формат API без обновления бота и веба

##  Инструкции для AI

### При работе с ботом
- Изучи существующие handlers перед добавлением
- Используй FSM для многошаговых диалогов
- Данные сохраняй через API

### При работе с API
- Новые эндпоинты  в соответствующий router
- Валидация  через Pydantic schemas
- Изменения БД  через Alembic миграции

### При добавлении полей
1. Модель (api/models/)
2. Миграция Alembic
3. Pydantic схема
4. API endpoint
5. Bot handler
6. Web интерфейс
