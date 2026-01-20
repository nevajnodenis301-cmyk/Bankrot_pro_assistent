# 🚀 Инструкция по установке и запуску

## Требования

- Docker Desktop или Docker Engine + Docker Compose
- Git (опционально)

## Шаг 1: Настройка Telegram бота

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Шаг 2: Получение API ключей для AI

### Timeweb Cloud AI (рекомендуется)

1. Зарегистрируйтесь на [timeweb.cloud](https://timeweb.cloud)
2. Перейдите в раздел API
3. Создайте новый API ключ
4. Сохраните ключ

### YandexGPT (альтернатива)

1. Зарегистрируйтесь в [Yandex Cloud](https://cloud.yandex.ru)
2. Создайте каталог (folder)
3. Включите YandexGPT API
4. Получите API ключ и Folder ID

## Шаг 3: Настройка проекта

```bash
# Клонировать или скачать проект
cd bankrot_pro

# Создать .env файл из примера
cp .env.example .env

# Открыть .env для редактирования
nano .env  # или любой текстовый редактор
```

Заполните следующие переменные:

```env
# PostgreSQL - смените пароль!
POSTGRES_USER=bankrot
POSTGRES_PASSWORD=YourSecurePassword123!

# Security - сгенерируйте случайную строку 32+ символов
SECRET_KEY=your_random_secret_key_here_32_chars_minimum

# Telegram Bot - вставьте токен от BotFather
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# AI Provider
AI_PROVIDER=timeweb

# Timeweb
TIMEWEB_API_KEY=your_timeweb_api_key
TIMEWEB_API_URL=https://api.timeweb.cloud/v1

# ИЛИ YandexGPT
# AI_PROVIDER=yandexgpt
# YANDEXGPT_API_KEY=your_yandex_api_key
# YANDEXGPT_FOLDER_ID=your_folder_id
```

## Шаг 4: Запуск проекта

```bash
# Запустить все сервисы
docker compose up -d

# Дождаться запуска (может занять 1-2 минуты при первом запуске)
docker compose ps

# Просмотреть логи
docker compose logs -f
```

## Шаг 5: Инициализация базы данных

```bash
# Войти в контейнер API
docker compose exec api bash

# Выполнить миграции
alembic upgrade head

# Выйти
exit
```

## Шаг 6: Проверка работы

### Web-интерфейс
Откройте в браузере: http://localhost:8501

### API документация
Откройте в браузере: http://localhost:8000/docs

### Telegram бот
Откройте Telegram и найдите ваш бот по username

Отправьте команду `/start`

## Шаг 7: Создание шаблона документа (опционально)

Для генерации документов необходим файл `api/templates/bankruptcy_application.docx`

### Вариант 1: Создать вручную

1. Откройте Microsoft Word или LibreOffice
2. Создайте шаблон с плейсхолдерами (см. `api/templates/README_TEMPLATE.md`)
3. Сохраните как `bankruptcy_application.docx`
4. Скопируйте файл:

```bash
# Если файл на хосте
docker cp bankruptcy_application.docx bankrot_pro-api-1:/app/api/templates/
```

### Вариант 2: Использовать упрощенный шаблон

```bash
# Войти в контейнер
docker compose exec api bash

# Создать минимальный шаблон
cd api/templates
python3 << EOF
from docx import Document
doc = Document()
doc.add_heading('ЗАЯВЛЕНИЕ о признании банкротом', 0)
doc.add_paragraph('Дело № {{ case_number }}')
doc.add_paragraph('ФИО: {{ full_name }}')
doc.add_paragraph('Долг: {{ total_debt }} рублей')
doc.save('bankruptcy_application.docx')
EOF

exit
```

## Управление проектом

```bash
# Остановить все сервисы
docker compose stop

# Запустить снова
docker compose start

# Перезапустить сервис
docker compose restart api

# Просмотреть логи конкретного сервиса
docker compose logs -f bot

# Полностью удалить контейнеры (БД сохранится в volumes)
docker compose down

# Удалить всё, включая данные БД (ВНИМАНИЕ: удалит все дела!)
docker compose down -v
```

## Обновление кода

```bash
# Остановить сервисы
docker compose down

# Обновить код (git pull или скачать новую версию)
git pull

# Пересобрать контейнеры
docker compose build

# Запустить
docker compose up -d

# Выполнить новые миграции (если есть)
docker compose exec api alembic upgrade head
```

## Резервное копирование

### Бэкап базы данных

```bash
# Создать дамп БД
docker compose exec postgres pg_dump -U bankrot bankrot > backup_$(date +%Y%m%d).sql

# Восстановить из дампа
docker compose exec -T postgres psql -U bankrot bankrot < backup_20240119.sql
```

### Бэкап всех данных

```bash
# Создать полный бэкап
docker compose exec postgres pg_dump -U bankrot bankrot > db_backup.sql
docker cp bankrot_pro-postgres-1:/var/lib/postgresql/data ./postgres_data_backup
```

## Проблемы и решения

### Бот не отвечает
- Проверьте логи: `docker compose logs bot`
- Убедитесь, что API запущен: `docker compose ps`
- Проверьте токен в `.env`

### API не запускается
- Проверьте подключение к БД: `docker compose logs postgres`
- Проверьте переменные окружения в `.env`
- Пересоздайте контейнеры: `docker compose up -d --force-recreate`

### Web-интерфейс не загружается
- Проверьте, что API доступен: http://localhost:8000/health
- Проверьте логи: `docker compose logs web`
- Очистите кеш браузера

### Ошибки миграций
```bash
# Откатить все миграции
docker compose exec api alembic downgrade base

# Применить заново
docker compose exec api alembic upgrade head
```

### Порты заняты
Измените порты в `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # API
  - "8502:8501"  # Web
```

## Полезные команды

```bash
# Проверить статус всех сервисов
docker compose ps

# Войти в контейнер
docker compose exec api bash
docker compose exec bot bash

# Посмотреть использование ресурсов
docker stats

# Очистить неиспользуемые образы
docker system prune

# Перезагрузить конфигурацию без пересборки
docker compose up -d --no-deps --build api
```

## Production deployment

Для production рекомендуется:

1. Использовать внешнюю PostgreSQL БД
2. Настроить HTTPS (nginx + Let's Encrypt)
3. Использовать управляемый Redis (например, Redis Cloud)
4. Настроить мониторинг (Prometheus + Grafana)
5. Настроить регулярные бэкапы
6. Использовать secrets вместо .env файла
7. Ограничить доступ к API через firewall

Для помощи с production deployment создайте Issue в репозитории.
