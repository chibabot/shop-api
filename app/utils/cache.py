import time
from functools import wraps
from flask import request, jsonify

# Словарь для хранения кэша
cache_store = {}
# Время жизни кэша в секундах (5 минут)
CACHE_TTL = 300

def generate_cache_key(prefix, **kwargs):
    """
    Генерирует ключ кэша на основе префикса и переданных параметров
    """
    sorted_kwargs = sorted(kwargs.items())
    params_str = '&'.join(f"{k}={v}" for k, v in sorted_kwargs)
    return f"{prefix}:{params_str}"

def set_cache(key, data):
    """
    Сохраняет данные в кэш с текущим временем
    """
    cache_store[key] = {
        'data': data,
        'timestamp': time.time()
    }

def get_cache(key):
    """
    Получает данные из кэша, если они существуют и не устарели
    """
    if key not in cache_store:
        return None
    
    cache_entry = cache_store[key]
    current_time = time.time()
    
    # Проверяем, не устарел ли кэш
    if current_time - cache_entry['timestamp'] > CACHE_TTL:
        # Удаляем устаревшую запись
        del cache_store[key]
        return None
    
    return cache_entry['data']

def clear_cache():
    """
    Очищает весь кэш
    """
    cache_store.clear()

def cached(prefix):
    """
    Декоратор для кэширования результатов функций
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Для GET запросов берем параметры из request.args
            if request.method == 'GET':
                cache_params = {k: v for k, v in request.args.items()}
                cache_key = generate_cache_key(prefix, **cache_params)
                
                # Проверяем наличие в кэше
                cached_data = get_cache(cache_key)
                if cached_data:
                    # Если данные есть в кэше, возвращаем их
                    print(f"Cache hit for {cache_key}")
                    return jsonify(cached_data), 200
            
            # Если кэша нет или не GET запрос, выполняем функцию
            result, status_code = func(*args, **kwargs)
            
            # Кэшируем только успешные GET запросы
            if request.method == 'GET' and status_code == 200:
                cache_key = generate_cache_key(prefix, **cache_params)
                set_cache(cache_key, result.json)
                print(f"Cached result for {cache_key}")
            
            return result, status_code
        return wrapper
    return decorator 