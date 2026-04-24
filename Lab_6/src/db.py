import psycopg2
import psycopg2.extras
import os
from src.logger import (info_logger, er_logger)


class DateBase:
    def __init__(self, database_url: str = None) -> None:
        self.database_url = database_url or os.environ.get(
            'DATABASE_URL',
            'postgresql://cloring:devpassword@cloring-postgresql:5432/cloring_dev'
        )

    def __repr__(self) -> str:
        return 'Class DateBase'

    def _connect(self):
        return psycopg2.connect(self.database_url)

    def create_users_table(self) -> None:
        """
        Создает таблицу users с нижеуказанными полями, если она не существует.
        """
        with self._connect() as con:
            cursor = con.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                            user_id SERIAL PRIMARY KEY,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL,
                            phone_number TEXT NULL )""")
            con.commit()
            info_logger.info(
                "The table 'users' has been created. Columns: user_id, email, password, phone_number")

    def select(self, fields: str, table_name: str, where: str = '') -> list[tuple]:
        """Делает выборку полей fields из таблицы table_name с доп условием where.

        Args:
            fields (str): поля для выборки
            table_name (str): имя таблицы
            where (str, optional): условие выбора полей если существует. Defaults to ''.

        Returns:
            list[tuple]: список кортежей значений
        """
        with self._connect() as con:
            cursor = con.cursor()
            if where:
                request = f'SELECT {fields} FROM {table_name} WHERE {where}'
                cursor.execute(request)
                info_logger.info(
                    f"Request completed: SELECT {fields} FROM {table_name} WHERE {where}")
            else:
                request = f'SELECT {fields} FROM {table_name}'
                cursor.execute(request)
                info_logger.info(
                    f"Request completed: SELECT {fields} FROM {table_name}")
            return cursor.fetchall()

    def insert(self, table_name: str, fields: str, values: str) -> bool:
        """Вставляет запись в таблицу.

        Args:
            table_name (str): имя таблицы
            fields (str): поля таблицы
            values (str): значения полей
        """
        with self._connect() as con:
            cursor = con.cursor()
            request = f'INSERT INTO {table_name} ({fields}) VALUES({values})'
            cursor.execute(request)
            con.commit()
            info_logger.info(
                f"Insertion is successful: INSERT INTO {table_name} ({fields}) VALUES({values})")
        return True

    def update_table(self, table_name: str, fields: list, new_values: list, condition: str = '') -> bool:
        try:
            with self._connect() as con:
                cursor = con.cursor()
                request = f'UPDATE {table_name} SET '
                for field, value in zip(fields, new_values):
                    request += f'{field}={value},'
                request = request[:-1]
                if condition:
                    request += f' WHERE {condition}'
                cursor.execute(request)
                con.commit()
                info_logger.info(f"Table has been updated. Request: {request}")
                return True
        except Exception:
            er_logger.error(
                f"Some error with table update. Request: {request}")
            return False

    def create_table_users_items(self):
        """
        Создает таблицу users_items с нижеуказанными полями, если она не существует.
        """
        with self._connect() as con:
            cursor = con.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS users_items (
                            item_id SERIAL PRIMARY KEY,
                            user_id INTEGER,
                            clothes_name TEXT NOT NULL,
                            clothes_category TEXT NOT NULL,
                            clothes_size TEXT NOT NULL,
                            clothes_condition TEXT NOT NULL,
                            clothes_brand TEXT,
                            clothes_material TEXT,
                            clothes_color TEXT,
                            clothes_description TEXT,
                            clothes_link_to_photo TEXT,
                           FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE)""")
            con.commit()
            info_logger.info(
                "The table 'users_items' has been successfully created.")
