import shlex
from typing import List
from .core import create_table, drop_table, list_tables, show_table_structure, METADATA_FILE
from .utils import load_metadata, save_metadata

def print_help():
    """Выводит справочную информацию по командам."""
    print("\nДоступные команды:")
    print("  create_table <table_name> <column1:type1> [column2:type2 ...] - Создать таблицу")
    print("  drop_table <table_name> - Удалить таблицу")
    print("  list_tables - Показать все таблицы")
    print("  show_table <table_name> - Показать структуру таблицы")
    print("  help - Показать эту справку")
    print("  exit - Выйти из программы")
    print("\nПример: create_table users name:str age:int active:bool")

def parse_columns(column_args: List[str]) -> List[tuple]:
    """
    Парсит аргументы столбцов в формате name:type.
    
    Args:
        column_args: Список аргументов столбцов
        
    Returns:
        Список кортежей (имя, тип)
        
    Raises:
        ValueError: Если формат неверный
    """
    columns = []
    for col_arg in column_args:
        if ':' not in col_arg:
            raise ValueError(f"Неверный формат столбца: {col_arg}. Используйте name:type")
        
        name, col_type = col_arg.split(':', 1)
        columns.append((name.strip(), col_type.strip()))
    
    return columns

def run():
    """Главная функция запуска БД с основным циклом."""
    print("Primitive Database запущена!")
    print("Введите 'help' для списка команд или 'exit' для выхода.")
    
    while True:
        try:
            metadata = load_metadata(METADATA_FILE)
            
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
                
            args = shlex.split(user_input)
            command = args[0].lower()
            
            if command == "exit":
                print("Выход из программы. До свидания!")
                break
                
            elif command == "help":
                print_help()
                
            elif command == "create_table":
                if len(args) < 3:
                    print("Ошибка: Используйте: create_table <table_name> <column1:type1> [column2:type2 ...]")
                    continue
                
                table_name = args[1]
                column_args = args[2:]
                
                try:
                    columns = parse_columns(column_args)
                    metadata = create_table(metadata, table_name, columns)
                    save_metadata(METADATA_FILE, metadata)
                    print(f"Таблица '{table_name}' успешно создана!")
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    
            elif command == "drop_table":
                if len(args) != 2:
                    print("Ошибка: Используйте: drop_table <table_name>")
                    continue
                
                table_name = args[1]
                
                try:
                    metadata = drop_table(metadata, table_name)
                    save_metadata(METADATA_FILE, metadata)
                    print(f"Таблица '{table_name}' успешно удалена!")
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    
            elif command == "list_tables":
                tables = list_tables(metadata)
                if tables:
                    print("Таблицы в базе данных:")
                    for table in tables:
                        print(f"  - {table}")
                else:
                    print("В базе данных нет таблиц.")
                    
            elif command == "show_table":
                if len(args) != 2:
                    print("Ошибка: Используйте: show_table <table_name>")
                    continue
                
                table_name = args[1]
                
                try:
                    structure = show_table_structure(metadata, table_name)
                    print(f"Структура таблицы '{table_name}':")
                    for col_name, col_type in structure["columns"]:
                        print(f"  - {col_name}: {col_type}")
                except ValueError as e:
                    print(f"Ошибка: {e}")
                    
            else:
                print(f"Неизвестная команда: {command}")
                print("Введите 'help' для списка команд.")
                
        except KeyboardInterrupt:
            print("\n\nВыход из программы. До свидания!")
            break
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")