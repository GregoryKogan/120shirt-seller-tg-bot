import sqlite3
from sqlite3 import Error
from config import DB_URI
import datetime


class DBCommunicator:
    def __init__(self):
        self.connection = self.create_connection(f"./{DB_URI}")
        self.cursor = self.connection.cursor() if self.connection else None

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

        self.checks_table.create_table()

        self.connection.commit()
        print("All SQLite tables created successfully")


class ChecksTable:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            bill_id VARCHAR NOT NULL,
            comment VARCHAR NOT NULL,
            created_at VARCHAR NOT NULL,
            status VARCHAR NOT NULL DEFAULT 'UNPAID'
        );"""

        with self.connection:
            self.cursor.execute(create_table_query)
        print("SQLite 'checks' table created")

    def add_check(self, user_id: int, amount: float, bill_id: str, comment: str):
        created_at = datetime.datetime.now().isoformat()
        with self.connection:
            return self.cursor.execute(
                """INSERT INTO checks (user_id, amount, bill_id, comment, created_at) 
                VALUES (:user_id, :amount, :bill_id, :comment, :created_at)""",
                {
                    "user_id": user_id,
                    "amount": amount,
                    "bill_id": bill_id,
                    "comment": comment,
                    "created_at": created_at,
                },
            )

    def get_check(self, bill_id: str):
        with self.connection:
            res = self.cursor.execute(
                "SELECT * FROM checks WHERE bill_id = :bill_id", {"bill_id": bill_id}
            ).fetchmany(1)
        return (
            None
            if len(res) == 0
            else {
                "user_id": res[0][1],
                "amount": res[0][2],
                "bill_id": res[0][3],
                "comment": res[0][4],
                "created_at": res[0][5],
                "status": res[0][6],
            }
        )

    def pay_check(self, bill_id):
        with self.connection:
            return self.cursor.execute(
                "UPDATE checks SET status = 'PAID' WHERE bill_id = :bill_id",
                {"bill_id": bill_id},
            )
