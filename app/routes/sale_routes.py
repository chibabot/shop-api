from flask import Blueprint, request, jsonify
from app import db
from app.models.models import Sale, Product
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, desc
from datetime import datetime as dt
from app.utils.cache import cached, clear_cache

sale_bp = Blueprint('sales', __name__)

@sale_bp.route('/sales', methods=['GET'])
def get_sales():
    try:
        sales = Sale.query.all()
        return jsonify({
            'success': True,
            'data': [sale.to_dict() for sale in sales]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales/<int:sale_id>', methods=['GET'])
def get_sale(sale_id):
    try:
        sale = Sale.query.get(sale_id)
        if not sale:
            return jsonify({
                'success': False,
                'message': f'Sale with id {sale_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': sale.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales', methods=['POST'])
def create_sale():
    try:
        data = request.get_json()
        
        if not data or 'product_id' not in data or 'quantity' not in data:
            return jsonify({
                'success': False,
                'message': 'Product ID and quantity are required'
            }), 400
        
        # Check if product exists
        product = Product.query.get(data['product_id'])
        if not product:
            return jsonify({
                'success': False,
                'message': f'Product with id {data["product_id"]} not found'
            }), 404
        
        # Check if enough stock available
        if product.stock < data['quantity']:
            return jsonify({
                'success': False,
                'message': 'Not enough stock available'
            }), 400
            
        # Update product stock
        product.stock -= data['quantity']
        
        sale_date = dt.fromisoformat(data['date']) if 'date' in data else dt.utcnow()
        
        new_sale = Sale(
            product_id=data['product_id'],
            quantity=data['quantity'],
            date=sale_date
        )
        
        db.session.add(new_sale)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sale recorded successfully',
            'data': new_sale.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    try:
        sale = Sale.query.get(sale_id)
        if not sale:
            return jsonify({
                'success': False,
                'message': f'Sale with id {sale_id} not found'
            }), 404
        
        data = request.get_json()
        old_quantity = sale.quantity
        
        if 'product_id' in data and data['product_id'] != sale.product_id:
            # Return the old product's stock
            old_product = Product.query.get(sale.product_id)
            if old_product:
                old_product.stock += old_quantity
                
            # Check if new product exists and has enough stock
            new_product = Product.query.get(data['product_id'])
            if not new_product:
                return jsonify({
                    'success': False,
                    'message': f'Product with id {data["product_id"]} not found'
                }), 404
                
            quantity_to_deduct = data.get('quantity', old_quantity)
            if new_product.stock < quantity_to_deduct:
                return jsonify({
                    'success': False,
                    'message': 'Not enough stock available for new product'
                }), 400
                
            new_product.stock -= quantity_to_deduct
            sale.product_id = data['product_id']
        
        if 'quantity' in data:
            product = Product.query.get(sale.product_id)
            # Calculate stock adjustment
            stock_adjustment = old_quantity - data['quantity']
            if stock_adjustment < 0 and abs(stock_adjustment) > product.stock:
                return jsonify({
                    'success': False,
                    'message': 'Not enough stock available'
                }), 400
                
            product.stock += stock_adjustment
            sale.quantity = data['quantity']
            
        if 'date' in data:
            sale.date = dt.fromisoformat(data['date'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sale updated successfully',
            'data': sale.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale(sale_id):
    try:
        sale = Sale.query.get(sale_id)
        if not sale:
            return jsonify({
                'success': False,
                'message': f'Sale with id {sale_id} not found'
            }), 404
        
        # Return quantity to product stock
        product = Product.query.get(sale.product_id)
        if product:
            product.stock += sale.quantity
            
        db.session.delete(sale)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sale deleted successfully'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales/total', methods=['GET'])
@cached('total_sales')
def get_total_sales():
    try:
        # Получаем параметры запроса
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Проверяем наличие обязательных параметров
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'message': 'Необходимо указать start_date и end_date'
            }), 400
            
        # Преобразуем строки в объекты datetime
        try:
            start_date = dt.fromisoformat(start_date_str)
            end_date = dt.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Неверный формат даты. Используйте ISO формат (YYYY-MM-DD или YYYY-MM-DDTHH:MM:SS)'
            }), 400
        
        # Получаем все продажи за указанный период
        # Учитываем скидку при расчете общей суммы продаж
        query = db.session.query(
            func.sum(Sale.quantity * Product.price * (1 - Sale.discount/100)).label('total_amount_with_discount'),
            func.avg(Sale.discount).label('avg_discount')
        ).join(
            Product, Sale.product_id == Product.product_id
        ).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        )
        
        result = query.first()
        total_sales = float(result.total_amount_with_discount) if result.total_amount_with_discount else 0
        avg_discount = round(float(result.avg_discount), 2) if result.avg_discount else 0
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date_str,
                    'end_date': end_date_str
                },
                'total_sales': round(total_sales, 2),
                'avg_discount': avg_discount
            }
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales/top-products', methods=['GET'])
@cached('top_products')
def get_top_products():
    try:
        # Получаем параметры запроса
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        limit_str = request.args.get('limit', '5')  # По умолчанию топ-5
        
        # Проверяем наличие обязательных параметров
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'message': 'Необходимо указать start_date и end_date'
            }), 400
            
        # Проверяем и преобразуем limit
        try:
            limit = int(limit_str)
            if limit <= 0:
                raise ValueError("Limit должен быть положительным числом")
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Неверный формат limit. Должно быть положительное целое число'
            }), 400
            
        # Преобразуем строки в объекты datetime
        try:
            start_date = dt.fromisoformat(start_date_str)
            end_date = dt.fromisoformat(end_date_str)
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Неверный формат даты. Используйте ISO формат (YYYY-MM-DD или YYYY-MM-DDTHH:MM:SS)'
            }), 400
        
        # Получаем топ продуктов по продажам за указанный период
        # Учитываем скидку при расчете общей суммы продаж
        query = db.session.query(
            Product.product_id,
            Product.name,
            Product.price,
            func.sum(Sale.quantity).label('total_quantity'),
            func.avg(Sale.discount).label('avg_discount'),
            func.sum(Sale.quantity * Product.price * (1 - Sale.discount/100)).label('total_amount_with_discount')
        ).join(
            Sale, Product.product_id == Sale.product_id
        ).filter(
            Sale.date >= start_date,
            Sale.date <= end_date
        ).group_by(
            Product.product_id
        ).order_by(
            desc('total_quantity')
        ).limit(limit)
        
        results = query.all()
        
        top_products = [{
            'product_id': product.product_id,
            'name': product.name,
            'price': float(product.price),
            'total_quantity': product.total_quantity,
            'avg_discount': round(product.avg_discount, 2) if product.avg_discount else 0.0,
            'total_amount_with_discount': round(float(product.total_amount_with_discount), 2) if product.total_amount_with_discount else 0.0
        } for product in results]
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date_str,
                    'end_date': end_date_str
                },
                'limit': limit,
                'top_products': top_products
            }
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@sale_bp.route('/sales/cache/clear', methods=['POST'])
def clear_sales_cache():
    try:
        clear_cache()
        return jsonify({
            'success': True,
            'message': 'Кэш очищен успешно'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500 