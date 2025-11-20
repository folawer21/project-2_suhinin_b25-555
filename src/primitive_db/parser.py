import shlex
from typing import Any, Dict, List, Tuple


def parse_where_clause(where_str: str) -> Dict[str, Any]:
    if not where_str:
        return {}

    try:
        parts = shlex.split(where_str)
        if len(parts) != 3 or parts[1] != "=":
            raise ValueError("Неверный формат WHERE. Используйте: column = value")

        column = parts[0]
        value_str = parts[2]

        value = parse_value(value_str)

        return {column: value}
    except Exception as e:
        raise ValueError(f"Ошибка парсинга WHERE: {e}")


def parse_set_clause(set_str: str) -> Dict[str, Any]:
    if not set_str:
        return {}

    result = {}
    try:
        assignments = [a.strip() for a in set_str.split(",")]

        for assignment in assignments:
            parts = shlex.split(assignment)
            if len(parts) != 3 or parts[1] != "=":
                raise ValueError(f"Неверный формат SET: {assignment}")

            column = parts[0]
            value_str = parts[2]
            value = parse_value(value_str)

            result[column] = value

    except Exception as e:
        raise ValueError(f"Ошибка парсинга SET: {e}")

    return result


def parse_value(value_str: str) -> Any:
    value_str = value_str.strip()

    if value_str.lower() in ("true", "false"):
        return value_str.lower() == "true"

    if value_str.isdigit() or (value_str[0] == "-" and value_str[1:].isdigit()):
        return int(value_str)

    try:
        return float(value_str)
    except ValueError:
        pass

    if (value_str.startswith('"') and value_str.endswith('"')) or (
        value_str.startswith("'") and value_str.endswith("'")
    ):
        return value_str[1:-1]

    return value_str


def parse_insert_values(
    values_str: str, expected_types: Dict[str, str]
) -> Tuple[List[Any], List[str]]:
    """Парсит значения для INSERT и проверяет их типы."""
    values = []
    errors = []

    try:
        parsed_values = shlex.split(values_str)

        columns = list(expected_types.keys())[1:]

        if len(parsed_values) != len(columns):
            error_msg = (
                f"Ожидается {len(columns)} значений, "
                f"получено {len(parsed_values)}"
            )
            errors.append(error_msg)
            return values, errors

        for i, (col_name, expected_type) in enumerate(zip(columns, parsed_values)):
            try:
                parsed_value = parse_value(expected_type)

                if expected_type == "int" and not isinstance(parsed_value, int):
                    error_msg = (
                        f"Столбец '{col_name}' должен быть int, "
                        f"получено: {expected_type}"
                    )
                    errors.append(error_msg)
                elif expected_type == "bool" and not isinstance(parsed_value, bool):
                    error_msg = (
                        f"Столбец '{col_name}' должен быть bool, "
                        f"получено: {expected_type}"
                    )
                    errors.append(error_msg)

                values.append(parsed_value)

            except Exception as e:
                error_msg = (
                    f"Ошибка парсинга значения '{expected_type}' "
                    f"для столбца '{col_name}': {e}"
                )
                errors.append(error_msg)

    except Exception as e:
        errors.append(f"Ошибка разбора значений: {e}")

    return values, errors