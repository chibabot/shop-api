from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация маршрутов
    from app.routes.category_routes import category_bp
    from app.routes.product_routes import product_bp
    from app.routes.sale_routes import sale_bp
    
    app.register_blueprint(category_bp, url_prefix='/api')
    app.register_blueprint(product_bp, url_prefix='/api')
    app.register_blueprint(sale_bp, url_prefix='/api')
    
    @app.route('/status')
    def status_check():
        return {'status': 'OK'}, 200
        
    return app 