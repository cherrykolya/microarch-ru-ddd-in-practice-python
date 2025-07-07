[![codecov](https://codecov.io/gh/cherrykolya/microarch-ru-ddd-in-practice-python/branch/main/graph/badge.svg)](https://codecov.io/gh/cherrykolya/microarch-ru-ddd-in-practice-python)

# Демонстрационный проект Domain Driven Design и Clean Architecture на Python

Этот проект демонстрирует применение принципов Domain Driven Design (DDD) и Clean Architecture в Python. Проект реализует систему доставки с использованием современных Python-фреймворков и инструментов.

📚 Подробнее о курсе: [microarch.ru/courses/ddd/languages/csharp](http://microarch.ru/courses/ddd/languages/csharp)

## Основные команды

```bash
# Установка зависимостей
poetry install && poetry shell

# Docker
docker-compose up -d           # запуск всех сервисов
docker-compose down           # остановка всех сервисов
docker-compose up -d api      # запуск только API

# Миграции
poetry run alembic upgrade head          # применить все миграции
poetry run alembic revision -m "name"    # создать новую миграцию
poetry run alembic downgrade -1         # откатить последнюю миграцию

# Тесты
poetry run pytest                       # запуск всех тестов
```

## Архитектура проекта

Проект следует принципам Clean Architecture и DDD:

- `core/` - содержит бизнес-логику:
  - `domain/` - доменные модели, агрегаты и сервисы
  - `application/` - use cases и бизнес-операции
  - `ports/` - интерфейсы для внешних зависимостей
- `infrastructure/` - реализация портов и технические детали:
  - `adapters/` - реализации для баз данных, очередей и внешних сервисов
  - `config/` - конфигурация приложения
  - `di/` - контейнер зависимостей и инъекция зависимостей
- `api/` - HTTP API и другие точки входа в приложение
- `tests/` - модульные и интеграционные тесты

## Основные технологии

| Технология | Версия | Описание | Документация |
|------------|---------|-----------|--------------|
| FastAPI | ^0.104.0 | Современный веб-фреймворк для создания API с автоматической OpenAPI документацией | [Docs](https://fastapi.tiangolo.com/) |
| SQLAlchemy | ^2.0.23 | Мощный ORM для работы с базами данных | [Docs](https://docs.sqlalchemy.org/en/20/) |
| Alembic | ^1.12.1 | Инструмент для управления миграциями базы данных | [Docs](https://alembic.sqlalchemy.org/) |
| Pydantic | ^2.5.0 | Библиотека для валидации данных и сериализации | [Docs](https://docs.pydantic.dev/) |
| gRPC | ^1.59.0 | Фреймворк для межсервисного взаимодействия | [Docs](https://grpc.io/docs/languages/python/) |
| aiokafka | ^0.10.0 | Асинхронный клиент для работы с Apache Kafka | [Docs](https://aiokafka.readthedocs.io/) |
| Pytest | ^7.4.3 | Фреймворк для модульного и интеграционного тестирования | [Docs](https://docs.pytest.org/) |
| Dependency Injector | ^4.41.0 | Библиотека для управления зависимостями и инверсии управления | [Docs](https://python-dependency-injector.ets-labs.org/) |
| Docker | N/A | Платформа для контейнеризации приложений | [Docs](https://docs.docker.com/) |
| Docker Compose | N/A | Инструмент для определения и запуска многоконтейнерных приложений | [Docs](https://docs.docker.com/compose/) |

## Лицензия

Код распространяется под лицензией [MIT](./LICENSE).
© 2025 microarch.ru
