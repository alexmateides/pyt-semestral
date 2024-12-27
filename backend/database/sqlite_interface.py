import sqlite3
import os
from dotenv import load_dotenv, find_dotenv


class SqliteInterface:
    """
    SQLite interface - simplifies connecting to database path
    """

    def __init__(self):
        load_dotenv(find_dotenv())
        database_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_database = os.path.join(database_dir, 'sqlite-database.db')
        self.connection = sqlite3.connect(self.path_database)
        self.cursor = self.connection.cursor()

    def exec(self, query: str) -> None:
        """
        Executes SQL query
        Args:
            query: SQL query to execute
        Returns:
        """
        self.cursor.execute(query)
