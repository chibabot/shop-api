from app import create_app, db
from app.models.models import Category, Product, Sale
import random
from datetime import datetime, timedelta
import uuid

def seed_data():
    app = create_app('default')
    with app.app_context():
        # Проверка наличия данных, чтобы избежать дублирования
        if Category.query.count() > 0:
            print("База данных уже содержит данные. Отмена заполнения.")
            return

        print("Начало заполнения базы данных...")
        
        # 1. Создание категорий
        categories = [
            Category(name="Electronics", description="Электронные устройства и гаджеты"),
            Category(name="Clothing", description="Одежда разных стилей и сезонов"),
            Category(name="Books", description="Книги различных жанров и форматов"),
            Category(name="Home", description="Товары для дома и интерьера"),
            Category(name="Sports", description="Спортивный инвентарь и аксессуары")
        ]
        
        db.session.add_all(categories)
        db.session.commit()
        print(f"Добавлено {len(categories)} категорий")
        
        # 2. Создание продуктов
        products = []
        
        # Electronics
        products.extend([
            Product(name="Laptop", description="Мощный ноутбук для работы и игр", price=1200.00, stock=15, category_id=1),
            Product(name="Smartphone", description="Современный смартфон с отличной камерой", price=800.00, stock=25, category_id=1),
            Product(name="Tablet", description="Планшет для работы и развлечений", price=450.00, stock=20, category_id=1),
            Product(name="Headphones", description="Беспроводные наушники с шумоподавлением", price=180.00, stock=30, category_id=1),
            Product(name="Smart Watch", description="Умные часы с трекером активности", price=250.00, stock=18, category_id=1),
            Product(name="Camera", description="Цифровая камера высокого разрешения", price=700.00, stock=10, category_id=1)
        ])
        
        # Clothing
        products.extend([
            Product(name="T-shirt", description="Хлопковая футболка базового стиля", price=25.00, stock=40, category_id=2),
            Product(name="Jeans", description="Классические джинсы прямого кроя", price=65.00, stock=35, category_id=2),
            Product(name="Jacket", description="Легкая куртка для прохладной погоды", price=120.00, stock=15, category_id=2),
            Product(name="Sneakers", description="Удобные кроссовки для повседневной носки", price=80.00, stock=20, category_id=2),
            Product(name="Sweater", description="Теплый свитер из мягкой шерсти", price=55.00, stock=25, category_id=2),
            Product(name="Dress", description="Элегантное платье для особых случаев", price=110.00, stock=12, category_id=2)
        ])
        
        # Books
        products.extend([
            Product(name="Novel", description="Современный роман известного автора", price=18.00, stock=30, category_id=3),
            Product(name="Textbook", description="Учебник по программированию", price=45.00, stock=20, category_id=3),
            Product(name="Cookbook", description="Книга рецептов мировой кухни", price=22.00, stock=25, category_id=3),
            Product(name="Biography", description="Биография выдающейся личности", price=24.00, stock=15, category_id=3),
            Product(name="Children's Book", description="Иллюстрированная книга для детей", price=15.00, stock=40, category_id=3),
            Product(name="Self-Help", description="Книга по саморазвитию", price=19.00, stock=35, category_id=3)
        ])
        
        # Home
        products.extend([
            Product(name="Lamp", description="Современная настольная лампа", price=65.00, stock=18, category_id=4),
            Product(name="Pillow", description="Мягкая подушка для комфортного сна", price=30.00, stock=25, category_id=4),
            Product(name="Blanket", description="Теплый плед для уютных вечеров", price=45.00, stock=20, category_id=4),
            Product(name="Vase", description="Декоративная ваза для цветов", price=55.00, stock=15, category_id=4),
            Product(name="Coffee Table", description="Стильный журнальный столик", price=120.00, stock=10, category_id=4),
            Product(name="Kitchenware Set", description="Набор кухонных принадлежностей", price=85.00, stock=12, category_id=4)
        ])
        
        # Sports
        products.extend([
            Product(name="Yoga Mat", description="Нескользящий коврик для йоги", price=35.00, stock=25, category_id=5),
            Product(name="Dumbbells", description="Набор гантелей разного веса", price=70.00, stock=18, category_id=5),
            Product(name="Water Bottle", description="Спортивная бутылка для воды", price=15.00, stock=40, category_id=5),
            Product(name="Running Shoes", description="Кроссовки для бега с амортизацией", price=95.00, stock=20, category_id=5),
            Product(name="Fitness Tracker", description="Браслет для отслеживания активности", price=60.00, stock=25, category_id=5),
            Product(name="Tennis Racket", description="Теннисная ракетка для начинающих", price=50.00, stock=15, category_id=5)
        ])
        
        db.session.add_all(products)
        db.session.commit()
        print(f"Добавлено {len(products)} продуктов")
        
        # 3. Создание продаж за последние 6 месяцев
        sales = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)  # 6 месяцев
        
        all_products = Product.query.all()
        for product in all_products:
            # От 5 до 15 продаж для каждого продукта
            num_sales = random.randint(5, 15)
            for _ in range(num_sales):
                # Случайная дата в пределах 6 месяцев
                sale_date = start_date + timedelta(
                    days=random.randint(0, 180),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                # Случайное количество от 1 до 5
                quantity = random.randint(1, 5)
                
                sales.append(Sale(
                    product_id=product.product_id,
                    quantity=quantity,
                    date=sale_date
                ))
        
        db.session.add_all(sales)
        db.session.commit()
        print(f"Добавлено {len(sales)} продаж")
        
        print("База данных успешно заполнена!")

if __name__ == "__main__":
    seed_data() 