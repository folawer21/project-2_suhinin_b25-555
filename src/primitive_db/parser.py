import shlex
from typing import Dict, Any, Tuple, List

def parse_where_clause(where_str: str) -> Dict[str, Any]:
    """
    Парсит WHERE условие в формате "column = value".
    
    Args:
        where_str: Строка условия
        
    Returns:
        Словарь {column: value}
        
    Raises:
        ValueError: Если формат неверный
    """
    if not where_str:
        return {}
    
    try:
        parts = shlex.split(where_str)
        if len(parts) != 3 or parts[1] != '=':
            raise ValueError("Неверный формат WHERE. Используйте: column = value")
        
        column = parts[0]
        value_str = parts[2]
        
        value = parse_value(value_str)
        
        return {column: value}
    except Exception as e:
        raise ValueError(f"Ошибка парсинга WHERE: {e}")

def parse_set_clause(set_str: str) -> Dict[str, Any]:
    """
    Парсит SET условие в формате "column1 = value1, column2 = value2".
    
    Args:
        set_str: Строка условий SET
        
    Returns:
        Словарь {column: value}
        
    Raises:
        ValueError: Если формат неверный
    """
    if not set_str:
        return {}
    
    result = {}
    try:
        assignments = [a.strip() for a in set_str.split(',')]
        
        for assignment in assignments:
            parts = shlex.split(assignment)
            if len(parts) != 3 or parts[1] != '=':
                raise ValueError(f"Неверный формат SET: {assignment}")
            
            column = parts[0]
            value_str = parts[2]
            value = parse_value(value_str)
            
            result[column] = value
    
    except Exception as e:
        raise ValueError(f"Ошибка парсинга SET: {e}")
    
    return result

def parse_value(value_str: str) -> Any:
    """
    Парсит строковое значение в соответствующий тип.
    
    Args:
        value_str: Строковое значение
        
    Returns:
        Значение соответствующего типа
    """
    value_str = value_str.strip()
    
    if value_str.lower() in ('true', 'false'):
        return value_str.lower() == 'true'
    
    if value_str.isdigit() or (value_str[0] == '-' and value_str[1:].isdigit()):
        return int(value_str)
    
    try:
        return float(value_str)
    except ValueError:
        pass
    
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    return value_str

def parse_insert_values(values_str: str, expected_types: Dict[str, str]) -> Tuple[List[Any], List[str]]:
    """
    Парсит значения для INSERT и проверяет их типы.
    
    Args:
        values_str: Строка со значениями
        expected_types: Ожидаемые типы столбцов {column: type}
        
    Returns:
        Кортеж (список значений, список ошибок)
    """
    values = []
    errors = []
    
    try:
        parsed_values = shlex.split(values_str)
        
        columns = list(expected_types.keys())[1:]  # исключаем ID
        
        if len(parsed_values) != len(columns):
            errors.append(f"Ожидается {len(columns)} значений, получено {len(parsed_values)}")
            return values, errors
        
        for i, (col_name, expected_type) in enumerate(zip(columns, parsed_values)):
            try:
                parsed_value = parse_value(expected_type)
                
                if expected_type == 'int' and not isinstance(parsed_value, int):
                    errors.append(f"Столбец '{col_name}' должен быть int, получено: {expected_type}")
                elif expected_type == 'bool' and not isinstance(parsed_value, bool):
                    errors.append(f"Столбец '{col_name}' должен быть bool, получено: {expected_type}")
                
                values.append(parsed_value)
                
            except Exception as e:
                errors.append(f"Ошибка парсинга значения '{expected_type}' для столбца '{col_name}': {e}")
    
    except Exception as e:
        errors.append(f"Ошибка разбора значений: {e}")
    
    return values, errors