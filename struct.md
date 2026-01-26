eventnotify-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Точка входа, создание приложения FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Загрузка конфигурации из .env и других источников
│   │   ├── database.py         # Настройка подключения к БД (например, через SQLAlchemy)
│   │   └── scheduler.py        # Инициализация APScheduler для фоновых задач
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── events.py   # Ручки для работы с событиями (получение списка)
│   │       │   └── webhook.py  # Ручка для веб-хука от Telegram
│   │       └── api.py          # Маршрутизатор для всех эндпоинтов v1
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый класс для моделей SQLAlchemy
│   │   ├── user.py             # Модель "Пользователь" (chat_id, статус подписки)
│   │   └── event.py            # Модель "Событие" (кешированные данные от KudaGo)
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic-схемы для валидации данных о пользователе
│   │   └── event.py            # Pydantic-схемы для событий
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kudago_client.py    # Клиент для работы с API KudaGo
│   │   ├── telegram_bot.py     # Логика обработки команд бота и отправки сообщений
│   │   └── notification_service.py # Сервис для формирования и рассылки уведомлений
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── base.py             # Базовые CRUD-операции
│   │   ├── user.py             # CRUD-операции для модели пользователя
│   │   └── event.py            # CRUD-операции для модели события
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── scheduled.py        # Фоновые задачи (ежедневный сбор событий, рассылка)
│   └── dependencies.py         # Общие зависимости (например, get_db)
├── alembic/                    # (Опционально) Директория для миграций базы данных
│   └── versions/
├── tests/                      # Директория для тестов
├── .env                        # Файл переменных окружения
├── requirements.txt            # Список зависимостей
├── docker-compose.yml          # (Опционально) Конфигурация для Docker Compose
├── Dockerfile                  # (Опционально) Dockerfile
└── README.md
