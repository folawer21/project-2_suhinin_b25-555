from typing import Dict, List, Any, Tuple
from .utils import save_metadata, load_metadata

# Константы
METADATA_FILE = "db_meta.json"
VALID_TYPES = {"int", "str", "bool"}

def validate_column_type(col_type: str) -> bool:
    """Проверяет корректность типа данных столбца."""
    return col_type.lower() in VALID_TYPES

def create_table(metadata: Dict[str, Any], table_name: str, columns: List[Tuple[str, str]]) -> Dict[str, Any]:
    """
    Создает новую таблицу в метаданных.
    
    Args:
        metadata: Текущие метаданные БД
        table_name: Имя таблицы
        columns: Список кортежей (имя_столбца, тип)
        
    Returns:
        Обновленные метаданные
        
    Raises:
        ValueError: Если таблица уже существует или неверные типы данных
    """
    # Проверяем существование таблицы
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")
    
    # Добавляем автоматический столбец ID
    table_columns = [("ID", "int")]
    
    # Проверяем и добавляем пользовательские столбцы
    for col_name, col_type in columns:
        if not validate_column_type(col_type):
            raise ValueError(f"Неподдерживаемый тип данных: {col_type}. Допустимые типы: {', '.join(VALID_TYPES)}")
        table_columns.append((col_name, col_type.lower()))
    
    # Сохраняем структуру таблицы в метаданные
    metadata[table_name] = {
        "columns": table_columns,
        "data": []  # Здесь будут храниться данные таблицы
    }
    
    return metadata

def drop_table(metadata: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """
    Удаляет таблицу из метаданных.
    
    Args:
        metadata: Текущие метаданные БД
        table_name: Имя таблицы для удаления
        
    Returns:
        Обновленные метаданные
        
    Raises:
        ValueError: Если таблица не существует
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    del metadata[table_name]
    return metadata

def list_tables(metadata: Dict[str, Any]) -> List[str]:
    """
    Возвращает список всех таблиц.
    
    Args:
        metadata: Метаданные БД
        
    Returns:
        Список имен таблиц
    """
    return list(metadata.keys())

def show_table_structure(metadata: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """
    Показывает структуру таблицы.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        
    Returns:
        Структура таблицы
        
    Raises:
        ValueError: Если таблица не существует
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    return metadata[table_name]