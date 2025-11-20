from typing import Dict, List, Any, Tuple
from prettytable import PrettyTable
from .utils import save_metadata, load_metadata, load_table_data, save_table_data
from .parser import parse_where_clause, parse_set_clause, parse_insert_values
from .decorators import handle_db_errors, confirm_action, log_time, create_cacher

# Константы
METADATA_FILE = "db_meta.json"
VALID_TYPES = {"int", "str", "bool"}

# Создаем кэшер для запросов
query_cacher = create_cacher()

def validate_column_type(col_type: str) -> bool:
    return col_type.lower() in VALID_TYPES

@handle_db_errors
def create_table(metadata: Dict[str, Any], table_name: str, columns: List[Tuple[str, str]]) -> Dict[str, Any]:
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

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    del metadata[table_name]
    
    import os
    data_file = f"data/{table_name}.json"
    if os.path.exists(data_file):
        os.remove(data_file)
    
    return metadata

@handle_db_errors
def list_tables(metadata: Dict[str, Any]) -> List[str]:
    return list(metadata.keys())

@handle_db_errors
def show_table_structure(metadata: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    return metadata[table_name]

@handle_db_errors
@log_time
def insert(metadata: Dict[str, Any], table_name: str, values_str: str) -> List[Dict[str, Any]]:
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

@handle_db_errors
@log_time
def select(metadata: Dict[str, Any], table_name: str, where_str: str = None) -> List[Dict[str, Any]]:
    if table_name not in metadata:
        raise ValueError(f"Таблица '{table_name}' не существует")
    
    def _execute_select():
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
    
    cache_key = f"select_{table_name}_{where_str}"
    return query_cacher(cache_key, _execute_select)

@handle_db_errors
def update(metadata: Dict[str, Any], table_name: str, set_str: str, where_str: str) -> List[Dict[str, Any]]:
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

@handle_db_errors
@confirm_action("удаление записей")
def delete(metadata: Dict[str, Any], table_name: str, where_str: str) -> List[Dict[str, Any]]:
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