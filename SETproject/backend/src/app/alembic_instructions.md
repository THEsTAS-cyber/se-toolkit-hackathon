# Инструкции по созданию миграций

## Первоначальная настройка
После запуска контейнера БД выполните:

```bash
# Внутри контейнера backend
cd /app
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Создание новых миграций
После изменения моделей:

```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

## Откат миграций
```bash
alembic downgrade -1  # Откатить последнюю миграцию
alembic downgrade base  # Откатить все миграции
```
