# Primitive Database

Простая реляционная база данных с интерфейсом командной строки, реализованная на Python. Проект демонстрирует работу с файловым хранением, CRUD-операциями и продвинутыми возможностями Python.

## Установка

```bash
pip install project-2-suhinin-b25-555
Использование

После установки запустите базу данных командой:

bash
database
Управление таблицами

Создание таблицы


create_table <table_name> <column1:type1> [column2:type2 ...]
Пример:


create_table users name:str age:int active:bool
Удаление таблицы


drop_table <table_name>
Пример:


drop_table users
Просмотр таблиц


list_tables                    # Список всех таблиц
show_table <table_name>        # Структура таблицы
CRUD-операции

Добавление записи


insert <table_name> <value1> <value2> ...
Пример:


insert users "John Doe" 28 true
Выборка записей


select <table_name> [WHERE <condition>]
Примеры:


select users
select users WHERE age = 28
select users WHERE name = "John Doe"
Обновление записей


update <table_name> SET <set_clause> WHERE <where_clause>
Пример:


update users SET age = 29 WHERE name = "John Doe"
Удаление записей


delete <table_name> WHERE <where_clause>
Пример:


delete users WHERE age = 28
Поддерживаемые типы данных

int - целые числа
str - строки
bool - логические значения (true/false)
Новые возможности

Обработка ошибок

Все операции базы данных защищены от ошибок. Система автоматически обрабатывает:

Отсутствие файлов данных
Обращение к несуществующим таблицам и столбцам
Ошибки валидации данных
Непредвиденные исключения
Подтверждение действий

Опасные операции требуют подтверждения пользователя:

Удаление таблиц (drop_table)
Удаление записей (delete)
Мониторинг производительности

Автоматический замер времени выполнения операций
Кэширование результатов запросов для ускорения повторных выборок
Логирование времени выполнения операций работы с данными
Улучшенный пользовательский опыт

Красивый табличный вывод с помощью библиотеки PrettyTable
Централизованная обработка ошибок
Интуитивно понятные сообщения об ошибках
Пример сессии работы

bash
$ database
Primitive Database запущена!

> create_table employees name:str department:str salary:int
Таблица 'employees' успешно создана!

> insert employees "Alice Smith" "Engineering" 75000
Запись успешно добавлена в таблицу 'employees'
Функция insert выполнилась за 0.015 секунд

> insert employees "Bob Johnson" "Marketing" 65000
Запись успешно добавлена в таблицу 'employees'
Функция insert выполнилась за 0.012 секунд

> select employees
+----+-------------+------------+--------+
| ID |    name     | department | salary |
+----+-------------+------------+--------+
| 1  | Alice Smith | Engineering| 75000  |
| 2  | Bob Johnson | Marketing  | 65000  |
+----+-------------+------------+--------+
Функция select выполнилась за 0.008 секунд

> delete employees WHERE name = "Bob Johnson"
Вы уверены, что хотите выполнить "удаление записей"? [y/n]: y
Записи из таблицы 'employees' успешно удалены

> drop_table employees
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]: y
Таблица 'employees' успешно удалена!
Архитектура проекта

core.py - основная логика работы с таблицами и данными
engine.py - игровой цикл и парсинг команд
utils.py - работа с файлами (загрузка/сохранение)
parser.py - разбор сложных условий WHERE и SET
decorators.py - декораторы для обработки ошибок, подтверждения действий и кэширования

Демонстрация работы

https://asciinema.org/a/Rz0jxe57R1Zm7Y674uaM8UlLq