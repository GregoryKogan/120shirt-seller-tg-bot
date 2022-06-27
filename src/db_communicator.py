import sqlite3
from sqlite3 import Error
from config import DB_URI


class DBCommunicator:
    def __init__(self):
        self.connection = self.create_connection(f"./{DB_URI}")
        self.cursor = self.connection.cursor() if self.connection else None

        self.users_table = UsersTable(self.connection)
        self.checks_table = ChecksTable(self.connection)

        self.create_tables()

    @staticmethod
    def create_connection(db_file):
        try:
            sqlite_connection = sqlite3.connect(db_file)
            cursor = sqlite_connection.cursor()
            print("Database created and successfully connected to SQLite")

            sqlite_select_query = "select sqlite_version();"
            cursor.execute(sqlite_select_query)
            record = cursor.fetchall()
            print("SQLite version: ", record)
            cursor.close()

        except sqlite3.Error as error:
            print("Error creating SQLite database connection", error)
        finally:
            if sqlite_connection:
                return sqlite_connection

    def create_tables(self):
        if not self.cursor:
            raise RuntimeError("No SQLite cursor available")

        self.users_table.create_table()
        self.checks_table.create_table()

        self.connection.commit()
        print("All SQLite tables created successfully")


class UsersTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            money INTEGER NOT NULL DEFAULT 0
        );"""

        with self.connection:
            self.cursor.execute(create_table_query)
        print("SQLite 'users' table created")

    def user_exists(self, user_id: int) -> bool:
        with self.connection:
            res = self.cursor.execute(
                f"SELECT * FROM users WHERE user_id = {user_id}"
            ).fetchall()
        return bool(len(res))

    def add_user(self, user_id: int):
        with self.connection:
            return self.cursor.execute(
                f"INSERT INTO users (user_id) VALUES ({user_id})"
            )

    def user_get_money(self, user_id: int) -> int:
        with self.connection:
            res = self.cursor.execute(
                f"SELECT money FROM users WHERE user_id = {user_id}"
            ).fetchmany(1)
        return int(res[0][0])

    def user_set_money(self, user_id: int, amount: int):
        with self.connection:
            return self.cursor.execute(
                f"UPDATE users SET money = {amount} WHERE user_id = {user_id}"
            )


class ChecksTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            money INTEGER NOT NULL,
            bill_id VARCHAR NOT NULL
        );"""

        with self.connection:
            self.cursor.execute(create_table_query)
        print("SQLite 'checks' table created")

    def add_check(self, user_id: int, money: int, bill_id: str):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO checks (user_id, money, bill_id) VALUES (:user_id, :money, :bill_id)",
                {"user_id": user_id, "money": money, "bill_id": bill_id},
            )

    def get_check(self, bill_id: str) -> bool:
        with self.connection:
            res = self.cursor.execute(
                "SELECT * FROM checks WHERE bill_id = :bill_id", {"bill_id": bill_id}
            ).fetchmany(1)
        return None if len(res) == 0 else res[0]

    def delete_check(self, bill_id: str):
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM checks WHERE bill_id = :bill_id", {"bill_id": bill_id}
            )
