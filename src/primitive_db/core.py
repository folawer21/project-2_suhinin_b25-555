from typing import Dict, List, Any, Tuple
from prettytable import PrettyTable
from .utils import save_metadata, load_metadata, load_table_data, save_table_data
from .parser import parse_where_clause, parse_set_clause, parse_insert_values

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
    if table_name in metadata:
        raise ValueError(f"Таблица '{table_name}' уже существует")
    
    table_columns = [("ID", "int")]
    
    for col_name, col_type in columns:
        if not validate_column_type(col_type):
            raise ValueError(f"Неподдерживаемый тип данных: {col_type}. Допустимые типы: {', '.join(VALID_TYPES)}")
        table_columns.append((col_name, col_type.lower()))
    
    metadata[table_name] = {
        "columns": table_columns,
        "column_types": {col[0]: col[1] for col in table_columns}
    }
    
    save_table_data(table_name, [])
    
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
    
    import os
    data_file = f"data/{table_name}.json"
    if os.path.exists(data_file):
        os.remove(data_file)
    
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

def insert(metadata: Dict[str, Any], table_name: str, values_str: str) -> List[Dict[str, Any]]:
    """
    Вставляет новую запись в таблицу.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        values_str: Строка со значениями для вставки
        
    Returns:
        Обновленные данные таблицы
        
    Raises:
        ValueError: Если таблица не существует или неверные данные
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    table_data = load_table_data(table_name)
    
    table_schema = metadata[table_name]
    column_types = table_schema["column_types"]
    
    values, errors = parse_insert_values(values_str, column_types)
    if errors:
        raise ValueError("; ".join(errors))
    
    if table_data:
        new_id = max(record["ID"] for record in table_data) + 1
    else:
        new_id = 1
    
    new_record = {"ID": new_id}
    columns = list(column_types.keys())[1:]
    
    for i, column in enumerate(columns):
        new_record[column] = values[i]
    
    table_data.append(new_record)
    save_table_data(table_name, table_data)
    
    return table_data

def select(metadata: Dict[str, Any], table_name: str, where_str: str = None) -> List[Dict[str, Any]]:
    """
    Выбирает записи из таблицы.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        where_str: Условие WHERE (опционально)
        
    Returns:
        Список найденных записей
        
    Raises:
        ValueError: Если таблица не существует
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    table_data = load_table_data(table_name)
    
    if not where_str:
        return table_data
    
    where_clause = parse_where_clause(where_str)
    
    filtered_data = []
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        if match:
            filtered_data.append(record)
    
    return filtered_data

def update(metadata: Dict[str, Any], table_name: str, set_str: str, where_str: str) -> List[Dict[str, Any]]:
    """
    Обновляет записи в таблице.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        set_str: Условие SET
        where_str: Условие WHERE
        
    Returns:
        Обновленные данные таблицы
        
    Raises:
        ValueError: Если таблица не существует или неверные данные
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    table_data = load_table_data(table_name)
    
    set_clause = parse_set_clause(set_str)
    where_clause = parse_where_clause(where_str)
    
    table_schema = metadata[table_name]
    valid_columns = table_schema["columns"]
    valid_column_names = [col[0] for col in valid_columns]
    
    for column in set_clause.keys():
        if column not in valid_column_names:
            raise ValueError(f"Столбец '{column}' не существует в таблице '{table_name}'")
    
    updated_count = 0
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        
        if match:
            for column, new_value in set_clause.items():
                record[column] = new_value
            updated_count += 1
    
    if updated_count > 0:
        save_table_data(table_name, table_data)
    
    return table_data

def delete(metadata: Dict[str, Any], table_name: str, where_str: str) -> List[Dict[str, Any]]:
    """
    Удаляет записи из таблицы.
    
    Args:
        metadata: Метаданные БД
        table_name: Имя таблицы
        where_str: Условие WHERE
        
    Returns:
        Обновленные данные таблицы
        
    Raises:
        ValueError: Если таблица не существует
    """
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    table_data = load_table_data(table_name)
    
    where_clause = parse_where_clause(where_str)
    
    new_data = []
    deleted_count = 0
    
    for record in table_data:
        match = True
        for column, value in where_clause.items():
            if column not in record or record[column] != value:
                match = False
                break
        
        if not match:
            new_data.append(record)
        else:
            deleted_count += 1
    
    if deleted_count > 0:
        save_table_data(table_name, new_data)
    
    return new_data

def format_table_output(data: List[Dict[str, Any]], columns: List[Tuple[str, str]]) -> str:
    """
    Форматирует данные таблицы для красивого вывода.
    
    Args:
        data: Данные таблицы
        columns: Столбцы таблицы
        
    Returns:
        Отформатированная строка таблицы
    """
    if not data:
        return "Нет данных для отображения"
    
    table = PrettyTable()
    table.field_names = [col[0] for col in columns]
    
    for record in data:
        row = []
        for col_name, _ in columns:
            row.append(record.get(col_name, ''))
        table.add_row(row)
    
    return str(table)