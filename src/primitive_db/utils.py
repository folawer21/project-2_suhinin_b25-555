import json
import os
from typing import Any, Dict, List

def load_metadata(filepath: str) -> Dict[str, Any]:
    """
    Загружает данные из JSON-файла.
    
    Args:
        filepath: Путь к JSON-файлу
        
    Returns:
        Словарь с метаданными или пустой словарь если файл не найден
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_metadata(filepath: str, data: Dict[str, Any]) -> None:
    """
    Сохраняет данные в JSON-файл.
    
    Args:
        filepath: Путь к JSON-файлу
        data: Данные для сохранения
    """
    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_table_data(table_name: str) -> List[Dict[str, Any]]:
    """
    Загружает данные таблицы из JSON-файла.
    
    Args:
        table_name: Имя таблицы
        
    Returns:
        Список записей таблицы или пустой список если файл не найден
    """
    filepath = f"data/{table_name}.json"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_table_data(table_name: str, data: List[Dict[str, Any]]) -> None:
    """
    Сохраняет данные таблицы в JSON-файл.
    
    Args:
        table_name: Имя таблицы
        data: Данные для сохранения
    """
    filepath = f"data/{table_name}.json"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)