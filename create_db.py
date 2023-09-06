import configparser
import os
import sqlite3
import sys
from sqlite3 import Error

import click


def create_table(db_path):
    """Создание базы данных."""

    sql_create_table = {
        'sql_software_registry_table': (
            '''
            CREATE TABLE IF NOT EXISTS software_registry_erp_ln (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subsystem TEXT,
                session_name TEXT,
                session_code TEXT,
                report_name TEXT,
                analyst TEXT,
                developer TEXT,
                client TEXT,
                navigator TEXT,
                date_technical_specs TEXT,
                date_development TEXT,
                note TEXT
            );
            '''
        ),
        'sql_stories_table': (
            '''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                development_id INTEGER,
                analyst TEXT,
                developer TEXT,
                date_last_change TEXT,
                note TEXT,
                is_initial TEXT,
                FOREIGN KEY (
                    development_id
                ) REFERENCES software_registry_erp_ln (id) ON DELETE CASCADE
            );
            '''
        ),
    }
    for _, sql_request in sql_create_table.items():
        run_query(db_path, sql_request)
    print('База данных создана!')


def run_query(db_path, query, data=(), import_csv=False):
    """Подключение и выполнение запросов к базе данных."""

    try:
        with sqlite3.connect(db_path) as connect:
            cursor = connect.cursor()
            if import_csv:
                cursor.executemany(query, data)
            else:
                cursor.execute(query, data)
            connect.commit()
    except Error as err:
        print(err)
        sys.exit()


if __name__ == '__main__':
    if not os.path.exists('settings.ini'):
        print('Упс, отсутствует файл settings.ini!')
        sys.exit()
    config = configparser.ConfigParser()
    try:
        config.read('settings.ini')
        datebase_path = config['DEFAULT']['datebase_path']
        data_path = config['DEFAULT']['data_path']
    except KeyError as err:
        print(
            'Упс, файл settings.ini содержит некорректные данные! '
            f'Отсутствует переменная: {err}.',
        )
        sys.exit()
    if os.path.exists(datebase_path):
        if click.confirm(
            'Обнаружен файл БД. Хотите создать новый файл и перезаписать '
            'данные? Процесс необратим!',
        ):
            os.remove(datebase_path)
            print('Старый файл БД был успешно удален!')
        else:
            print('Операция по созданию БД отменена.')
            sys.exit()
    create_table(datebase_path)
