# Wallet API
REST API для управления кошельками с поддержкой операций пополнения и снятия средств.
## Стек
- **FastAPI** - веб-фреймворк
- **SQLAlchemy** (async) - ORM
- **PostgreSQL** — база данных
- **asyncpg** — асинхронный драйвер PostgreSQL
- **Alembic** — миграции базы данных
- **Docker / Docker Compose** — контейнеризация
- **pytest** — тестирование
## Структура проекта
```
.
├── alembic/              # Миграции базы данных
│   ├── versions/
│   └── env.py
├── main.py               # Точка входа
├── config.py             # Настройки приложения
├── database.py           # Подключение к БД
├── models.py             # Модели SQLAlchemy
├── schema.py             # Схемы Pydantic
├── handlers.py           # Бизнес-логика
├── routes.py             # Эндпоинты
├── test_routes.py        # Тесты
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```
## Установка и запуск
### Настройка переменных окружения
Создать файл `.env` в корне проекта:
```env
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
DB_NAME=wallets
```
### Запуск
```bash
docker compose up --build
```
Приложение будет доступно на `http://localhost:8000`.
Документация Swagger: `http://localhost:8000/docs`.
## API
### Получить баланс кошелька
```
GET /api/v1/wallets/{wallet_uuid}
```
**Ответ:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": "1000.00"
}
```
### Изменить баланс кошелька
```
POST /api/v1/wallets/{wallet_uuid}/operation
```
**Тело запроса:**
```json
{
  "operation_type": "DEPOSIT",
  "amount": "500.00"
}
```
`operation_type` — `DEPOSIT` (пополнение) или `WITHDRAW` (снятие).
**Ответ:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "wallet_uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "operation_type": "DEPOSIT",
  "amount": "500.00",
  "status": "SUCCESS",
  "created_at": "2026-04-02T12:00:00Z"
}
```
### Коды ответов
| Код | Описание |
|-----|----------|
| 200 | Успешно |
| 400 | Недостаточно средств |
| 404 | Кошелёк не найден |
| 422 | Ошибка валидации |
## Тесты

Тесты используют моки и не требуют запущенной базы данных.

#### Локально
```bash
pip install pytest httpx
pytest test_routes.py -v
```

#### В контейнере
```bash
docker exec -it itk_task-app-1 pytest test_routes.py -v
```

## Миграции
Миграции применяются автоматически при запуске контейнера `migrations`.
Для создания новой миграции локально (требуется `DB_HOST=localhost` в `.env`):
```bash
alembic revision --autogenerate -m "название миграции"
```
