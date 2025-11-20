import shlex

from .core import (
    METADATA_FILE,
    create_table,
    delete,
    drop_table,
    format_table_output,
    insert,
    list_tables,
    select,
    show_table_structure,
    update,
)
from .utils import load_metadata, save_metadata


def print_help():
    print("\nДоступные команды:")
    print("  Управление таблицами:")
    print("    create_table <table_name> <column1:type1>")
    print("                    [column2:type2 ...] - Создать таблицу")
    print("    drop_table <table_name> - Удалить таблицу")
    print("    list_tables - Показать все таблицы")
    print("    show_table <table_name> - Показать структуру таблицы")
    print("  CRUD операции:")
    print("    insert <table_name> <value1> <value2> ... - Добавить запись")
    print("    select <table_name> [WHERE <condition>] - Показать записи")
    print("    update <table_name> SET <set_clause> WHERE <where_clause>")
    print("                    - Обновить записи")
    print("    delete <table_name> WHERE <where_clause> - Удалить записи")
    print("  Общие:")
    print("    help - Показать эту справку")
    print("    exit - Выйти из программы")
    print("\nПримеры:")
    print("  create_table users name:str age:int active:bool")
    print("  insert users 'John Doe' 28 true")
    print("  select users WHERE age = 28")
    print("  update users SET age = 29 WHERE name = 'John Doe'")
    print("  delete users WHERE age = 28")


def run():
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
                    print("Ошибка: Используйте: create_table <table_name>")
                    print("                    <column1:type1> [column2:type2 ...]")
                    continue

                table_name = args[1]
                column_args = args[2:]

                columns = []
                for col_arg in column_args:
                    if ":" not in col_arg:
                        print(f"Ошибка: Неверный формат столбца: {col_arg}.")
                        print("                    Используйте name:type")
                        break
                    name, col_type = col_arg.split(":", 1)
                    columns.append((name.strip(), col_type.strip()))
                else:
                    result = create_table(metadata, table_name, columns)
                    if result is not None:
                        save_metadata(METADATA_FILE, metadata)
                        print(f"Таблица '{table_name}' успешно создана!")

            elif command == "drop_table":
                if len(args) != 2:
                    print("Ошибка: Используйте: drop_table <table_name>")
                    continue

                table_name = args[1]

                result = drop_table(metadata, table_name)
                if result is not None:
                    save_metadata(METADATA_FILE, metadata)
                    print(f"Таблица '{table_name}' успешно удалена!")

            elif command == "list_tables":
                tables = list_tables(metadata)
                if tables is not None:
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

                structure = show_table_structure(metadata, table_name)
                if structure is not None:
                    print(f"Структура таблицы '{table_name}':")
                    for col_name, col_type in structure["columns"]:
                        print(f"  - {col_name}: {col_type}")

            elif command == "insert":
                if len(args) < 3:
                    print("Ошибка: Используйте: insert <table_name>")
                    print("                    <value1> <value2> ...")
                    continue

                table_name = args[1]
                values_str = " ".join(args[2:])

                result = insert(metadata, table_name, values_str)
                if result is not None:
                    print(f"Запись успешно добавлена в таблицу '{table_name}'")

            elif command == "select":
                if len(args) < 2:
                    print("Ошибка: Используйте: select <table_name>")
                    print("                    [WHERE <condition>]")
                    continue

                table_name = args[1]
                where_str = None

                if len(args) > 3 and args[2].lower() == "where":
                    where_str = " ".join(args[3:])
                elif len(args) > 2:
                    print("Ошибка: Используйте: select <table_name>")
                    print("                    [WHERE <condition>]")
                    continue

                data = select(metadata, table_name, where_str)
                if data is not None and table_name in metadata:
                    columns = metadata[table_name]["columns"]
                    print(format_table_output(data, columns))

            elif command == "update":
                if (len(args) < 6 or args[2].lower() != "set" 
                        or args[4].lower() != "where"):
                    print("Ошибка: Используйте: update <table_name>")
                    print("                    SET <set_clause> WHERE <where_clause>")
                    continue

                table_name = args[1]
                set_str = args[3]
                where_str = " ".join(args[5:])

                result = update(metadata, table_name, set_str, where_str)
                if result is not None:
                    print(f"Записи в таблице '{table_name}' успешно обновлены")

            elif command == "delete":
                if len(args) < 4 or args[2].lower() != "where":
                    print("Ошибка: Используйте: delete <table_name>")
                    print("                    WHERE <where_clause>")
                    continue

                table_name = args[1]
                where_str = " ".join(args[3:])

                result = delete(metadata, table_name, where_str)
                if result is not None:
                    print(f"Записи из таблицы '{table_name}' успешно удалены")

            else:
                print(f"Неизвестная команда: {command}")
                print("Введите 'help' для списка команд.")

        except KeyboardInterrupt:
            print("\n\nВыход из программы. До свидания!")
            break
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")