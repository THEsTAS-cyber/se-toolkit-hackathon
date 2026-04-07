# Настройка PSPricing API

## Обзор

Backend автоматически собирает данные о ценах игр в PlayStation Store из разных стран через PSPricing API каждые 12 часов.

## Конфигурация

Добавьте следующие переменные окружения в `.env` файл:

```bash
# Базовый URL API (по умолчанию используется демо-режим)
PSPRICING_BASE_URL=https://psprices.com/api/b2b/demo/

# Название коллекции для сбора данных
PSPRICING_COLLECTION=most-wanted-deals

# Список стран для мониторинга
PSPRICING_REGIONS=["ua","us","gb","de","fr","pl","tr","jp","br","au"]

# Интервал синхронизации в часах
PSPRICING_SYNC_INTERVAL_HOURS=12
```

## Поддерживаемые страны

Рекомендуемый список стран с разными валютами:
- `ua` - Украина (UAH)
- `us` - США (USD)
- `gb` - Великобритания (GBP)
- `de` - Германия (EUR)
- `fr` - Франция (EUR)
- `pl` - Польша (PLN)
- `tr` - Турция (TRY)
- `jp` - Япония (JPY)
- `br` - Бразилия (BRL)
- `au` - Австралия (AUD)

## API Endpoints

### Получение списка игр
```
GET /api/games
```
Возвращает список всех игр с их ценами по регионам.

### Получение конкретной игры
```
GET /api/games/{game_id}
```
Возвращает детальную информацию об игре со всеми ценами.

### Сравнение цен для игры
```
GET /api/games/{game_id}/prices
```
Возвращает цены игры во всех регионах для сравнения.

Пример ответа:
```json
{
  "game_id": 1,
  "name": "Cyberpunk 2077",
  "title_id": "PPSA04027_00",
  "cover_url": "https://...",
  "prices": [
    {
      "id": 1,
      "region": "ua",
      "currency": "UAH",
      "current_price": 674.55,
      "original_price": 1499,
      "discount_percent": 55,
      "ps_plus_price": null,
      "collection": "most-wanted-deals",
      "collected_at": "2026-04-05T12:00:00"
    },
    {
      "id": 2,
      "region": "us",
      "currency": "USD",
      "current_price": 19.99,
      "original_price": 59.99,
      "discount_percent": 67,
      "ps_plus_price": null,
      "collection": "most-wanted-deals",
      "collected_at": "2026-04-05T12:00:00"
    }
  ]
}
```

### Поиск игр
```
GET /api/games/search/?q=cyberpunk
```

### Сравнение игр по названию
```
GET /api/games/compare/?name=Cyberpunk
```
Находит все игры с похожим названием и возвращает их цены для сравнения.

## Ручной запуск синхронизации

Для немедленного запуска синхронизации (не ожидая 12 часов):

```python
# В Python консоли или через скрипт
import asyncio
from app.scheduler import scheduler

asyncio.run(scheduler.run_once_now())
```

Или через API (нужно добавить endpoint):
```
POST /api/admin/sync
```

## База данных

### Структура

**Таблица `games`:**
- `id` - уникальный идентификатор
- `ps_id` - ID из PSPricing API
- `sku` - артикул
- `title_id` - ID тайтла
- `concept_id` - ID концепта
- `name` - название игры
- `description` - описание
- `cover_url` - URL обложки
- `platforms` - платформы (PS4, PS5)
- `audio_languages` - языки аудио
- `subtitle_languages` - языки субтитров
- `release_date` - дата выхода
- `last_synced_at` - последняя синхронизация

**Таблица `price_entries`:**
- `id` - уникальный идентификатор
- `game_id` - ссылка на игру
- `region` - регион (ua, us, de, etc.)
- `currency` - валюта (UAH, USD, EUR, etc.)
- `current_price` - текущая цена
- `original_price` - оригинальная цена
- `discount_percent` - процент скидки
- `ps_plus_price` - цена для PS Plus
- `collection` - название коллекции
- `collected_at` - время сбора данных

### Инициализация БД

```bash
# Способ 1: Через SQL скрипт
psql -U $DB_USER -d $DB_NAME -f src/app/init_db.sql

# Способ 2: Через Python (создаст таблицы автоматически при запуске)
# В коде уже есть init_db(), который создаст таблицы
```

## Архитектура

```
scheduler.py (каждые 12 часов)
    ↓
price_sync.py (сервис синхронизации)
    ↓
pspricing.py (клиент API)
    ↓
models/game.py (модели БД)
```

### Как работает синхронизация

1. **Scheduler** запускает `PriceSyncService` каждые 12 часов
2. **PriceSyncService** создаёт `PSPricingClient` и запрашивает данные для каждого региона
3. **PSPricingClient** делает HTTP запросы к PSPricing API
4. **PriceSyncService** обрабатывает ответ:
   - Ищет существующую игру по `ps_id` или `title_id`
   - Если не найдена - создаёт новую
   - Создаёт запись о цене в `price_entries` для каждого региона
5. Все изменения сохраняются в транзакции

## Будущее расширение

Для сравнения цен игр в разных странах можно использовать:

```python
# Пример: Найти самую дешёвую страну для игры
from sqlalchemy import select
from app.models.game import Game, PriceEntry

async def find_cheapest_region(game_id: int):
    stmt = (
        select(PriceEntry)
        .where(PriceEntry.game_id == game_id)
        .order_by(PriceEntry.current_price.asc())
    )
    # Вернёт регион с самой низкой ценой
```
