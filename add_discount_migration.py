import os
import sys
import random
from flask_migrate import migrate, upgrade
from app import create_app, db
from app.models.models import Sale

def add_discount_migration():
    app = create_app('default')
    with app.app_context():
        # Создание миграции для добавления поля discount
        print("Создание миграции для поля discount...")
        migrate(message='add_discount_field')
        
        # Применение миграции
        print("Применение миграции...")
        upgrade()
        
        # Обновление существующих записей случайными значениями скидок
        print("Обновление существующих записей случайными значениями скидок...")
        
        sales = Sale.query.all()
        for sale in sales:
            # Генерация случайной скидки от 0% до 20%
            sale.discount = round(random.uniform(0, 20), 2)
        
        db.session.commit()
        print(f"Обновлено {len(sales)} записей продаж со случайными скидками.")
        
        print("Миграция успешно выполнена!")

if __name__ == '__main__':
    add_discount_migration() 