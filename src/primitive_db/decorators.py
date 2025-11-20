import time
from typing import Any, Callable, Dict
from functools import wraps

def handle_db_errors(func: Callable) -> Callable:
    """Декоратор для обработки ошибок базы данных."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper

def confirm_action(action_name: str) -> Callable:
    """Декоратор для подтверждения опасных операций."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            response = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ').strip().lower()
            if response != 'y':
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func: Callable) -> Callable:
    """Декоратор для замера времени выполнения функции."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {execution_time:.3f} секунд")
        return result
    return wrapper

def create_cacher() -> Callable:
    """Фабрика функций для кэширования результатов."""
    cache: Dict[str, Any] = {}
    
    def cache_result(key: str, value_func: Callable) -> Any:
        """Кэширует результат выполнения функции."""
        if key in cache:
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result
    
    return cache_result