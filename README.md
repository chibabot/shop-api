# Shop API

RESTful API для управления категориями, продуктами и продажами с функциями аналитики.

## Структура проекта

```
shop-api/
├── app/
│   ├── models/            # Модели данных SQLAlchemy
│   │   └── models.py      # Определения моделей (Category, Product, Sale)
│   ├── routes/            # API маршруты
│   │   ├── category_routes.py # Эндпоинты для категорий
│   │   ├── product_routes.py  # Эндпоинты для продуктов
│   │   └── sale_routes.py     # Эндпоинты для продаж и аналитики
│   ├── utils/             # Вспомогательные утилиты
│   │   └── cache.py       # Система кэширования
│   └── __init__.py        # Инициализация приложения
├── migrations/            # Миграции Alembic
├── config.py              # Конфигурация приложения
├── initial_data.py        # Скрипт для заполнения базы данных
├── Dockerfile             # Инструкции для сборки Docker-образа
├── docker-compose.yml     # Конфигурация для Docker Compose
├── requirements.txt       # Зависимости проекта
└── run.py                 # Точка входа для запуска приложения
```

## Требования

* Python 3.8+
* PostgreSQL 10+
* Зависимости из requirements.txt
* Docker и Docker Compose (опционально, для запуска в контейнере)

## Установка и настройка

### Локальная установка

1. Клонируйте репозиторий:
   ```
   git clone <url-репозитория>
   cd shop-api
   ```

2. Создайте и активируйте виртуальное окружение:
   ```
   python -m venv venv
   # Для Windows:
   venv\Scripts\activate
   # Для Linux/MacOS:
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

4. Создайте базу данных в PostgreSQL:
   ```
   createdb shop_api_db
   ```

5. Настройте соединение с PostgreSQL в `config.py`:
   ```python
   # Укажите свои учетные данные для доступа к PostgreSQL
   SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/shop_api_db'
   ```

6. Инициализируйте базу данных:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. Заполните базу данных начальными данными:
   ```
   python initial_data.py
   ```

### Установка с использованием Docker

1. Клонируйте репозиторий:
   ```
   git clone <url-репозитория>
   cd shop-api
   ```

2. Запустите приложение с помощью Docker Compose:
   ```
   docker-compose up --build
   ```

   Это автоматически:
   - Создаст и запустит контейнер с PostgreSQL
   - Соберет и запустит контейнер с приложением
   - Выполнит миграции базы данных
   - Заполнит базу данных начальными данными

3. Приложение будет доступно по адресу: `http://localhost:5000`

4. Для остановки контейнеров:
   ```
   docker-compose down
   ```

## Запуск API

### Локальный запуск

```
# Устанавливаем переменную окружения для Flask
# Для Windows:
set FLASK_APP=run.py
# Для Linux/MacOS:
export FLASK_APP=run.py

# Запуск сервера разработки
flask run
```

Или с помощью Python:
```
python run.py
```

### Запуск в Docker

```
docker-compose up
```

Сервер запустится на `http://localhost:5000`.

## API Endpoints

### Категории

* `GET /api/categories` - получить список всех категорий
* `GET /api/categories/<id>` - получить категорию по ID
* `POST /api/categories` - создать новую категорию
* `PUT /api/categories/<id>` - обновить категорию
* `DELETE /api/categories/<id>` - удалить категорию

### Продукты

* `GET /api/products` - получить список всех продуктов
* `GET /api/products/<id>` - получить продукт по ID
* `POST /api/products` - создать новый продукт
* `PUT /api/products/<id>` - обновить продукт
* `DELETE /api/products/<id>` - удалить продукт

### Продажи

* `GET /api/sales` - получить список всех продаж
* `GET /api/sales/<id>` - получить продажу по ID
* `POST /api/sales` - создать новую продажу
* `PUT /api/sales/<id>` - обновить продажу
* `DELETE /api/sales/<id>` - удалить продажу

### Аналитика

* `GET /api/sales/total` - получить общую сумму продаж за указанный период
  * Параметры: `start_date`, `end_date` (формат даты: ISO, например, "2023-01-01")
  * Пример: `/api/sales/total?start_date=2023-01-01&end_date=2023-06-30`

* `GET /api/sales/top-products` - получить топ самых продаваемых товаров
  * Параметры: `start_date`, `end_date`, `limit` (опционально, по умолчанию 5)
  * Пример: `/api/sales/top-products?start_date=2023-01-01&end_date=2023-06-30&limit=10`

* `POST /api/sales/cache/clear` - очистить кэш аналитических запросов

## Кэширование

API использует систему кэширования в памяти (in-memory) для оптимизации повторных аналитических запросов:

- Результаты запросов хранятся в кэше в течение 5 минут
- Для очистки кэша можно использовать эндпоинт `/api/sales/cache/clear`
- Кэширование применяется к эндпоинтам `/api/sales/total` и `/api/sales/top-products`

## Примеры запросов

### Создание категории

```
POST /api/categories
Content-Type: application/json

{
  "name": "Электроника",
  "description": "Электронные устройства и гаджеты"
}
```

### Создание продукта

```
POST /api/products
Content-Type: application/json

{
  "name": "Смартфон XYZ",
  "description": "Новейший смартфон с высококачественной камерой",
  "price": 999.99,
  "stock": 50,
  "category_id": 1
}
```

### Создание продажи

```
POST /api/sales
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2,
  "date": "2023-06-15T14:30:00",
  "discount": 5.5
}
```

### Получение статистики продаж

```
GET /api/sales/total?start_date=2023-01-01&end_date=2023-06-30
```

### Получение топ-продуктов

```
GET /api/sales/top-products?start_date=2023-01-01&end_date=2023-06-30&limit=3
```

## Модель данных

### Категории (categories)
- `category_id` (Integer, PK) - ID категории
- `name` (String) - Название категории
- `description` (Text) - Описание категории

### Продукты (products)
- `product_id` (Integer, PK) - ID продукта
- `name` (String) - Название продукта
- `description` (Text) - Описание продукта
- `price` (Numeric) - Цена продукта
- `stock` (Integer) - Количество на складе
- `category_id` (Integer, FK) - ID категории

### Продажи (sales)
- `sale_id` (Integer, PK) - ID продажи
- `product_id` (Integer, FK) - ID проданного продукта
- `quantity` (Integer) - Количество проданных единиц
- `date` (DateTime) - Дата и время продажи
- `discount` (Float) - Скидка (в процентах)

## Миграции

Проект использует Alembic для управления миграциями базы данных:

1. Создание новой миграции:
   ```
   flask db migrate -m "описание_миграции"
   ```

2. Применение миграций:
   ```
   flask db upgrade
   ```

3. Добавление скидок (для существующей базы):
   ```
   python add_discount_migration.py
   ```

## Обработка ошибок

API возвращает соответствующие HTTP-коды состояния и сообщения об ошибках в формате JSON:

```json
{
  "success": false,
  "message": "Описание ошибки"
}
```

Стандартные коды ошибок:
- 400: Некорректный запрос
- 404: Ресурс не найден
- 500: Внутренняя ошибка сервера 