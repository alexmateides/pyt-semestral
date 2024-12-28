"""
Interface for MongoDB database, currently not used
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv


class MongoDBInterface:
    """
    Interface for MongoDB database, used for .env compatibility -> removes the need for hardcoding
    This wrapper supports most MongoDB operations:

    - insert_one/many
    - find/find_one
    - update_one/update_manya
    - delete_one/delete_many
    - create_index
    """

    def __init__(self):
        # Load environment variables
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)

        # Connect to MongoDB
        self.client = MongoClient(os.getenv('MONGODB_HOST'))
        self.db = self.client[os.getenv('MONGODB_DATABASE')]

    def insert_one(self, collection: str, document: dict) -> None:
        """
        Inserts one document into the specified collection.

        Args:
            collection: Name of the collection.
            document: Document to be inserted.

        Returns: None
        """
        self.db[collection].insert_one(document)

    def insert_many(self, collection: str, documents: list) -> None:
        """
        Inserts many documents into the specified collection.

        Args:
            collection: Name of the collection.
            documents: List of documents to be inserted.

        Returns: None
        """
        self.db[collection].insert_many(documents)

    def find_one(self, collection: str, query: dict = None) -> dict:
        """
        Finds a single document matching the query in the specified collection.

        Args:
            collection: Name of the collection.
            query: Query to match the document.

        Returns: Matching document or None.
        """
        return self.db[collection].find_one(query)

    def find(self, collection: str, query: dict = None, projection: dict = None) -> list:
        """
        Finds all documents matching the query in the specified collection.

        Args:
            collection: Name of the collection.
            query: Query to match the documents.
            projection: Fields to include or exclude in the result (optional).

        Returns: List of matching documents.
        """
        cursor = self.db[collection].find(query, projection)
        return list(cursor)

    def update_one(self, collection: str, query: dict, update: dict) -> None:
        """
        Updates a single document matching the query in the specified collection.

        Args:
            collection: Name of the collection.
            query: Query to match the document.
            update: Update operations to apply.

        Returns: None
        """
        self.db[collection].update_one(query, update)

    def update_many(self, collection: str, query: dict, update: dict) -> None:
        """
        Updates multiple documents matching the query in the specified collection.

        Args:
            collection: Name of the collection.
            query: Query to match the documents.
            update: Update operations to apply.

        Returns: None
        """
        self.db[collection].update_many(query, update)

    def delete_one(self, collection: str, query: dict) -> None:
        """
        Deletes a single document matching the query in the specified collection.

        Args:
            collection: Name of the collection.
            query: Query to match the document.

        Returns: None
        """
        self.db[collection].delete_one(query)

    def delete_many(self, collection: str, query: dict) -> None:
        """
        Deletes multiple documents matching the query in the specified collection.

        Args:
            collection: Name of the collection.
            query: Query to match the documents.

        Returns: None
        """
        self.db[collection].delete_many(query)

    def create_index(self, collection: str, keys: list, unique: bool = False) -> str:
        """
        Creates an index on the specified keys in the collection.

        Args:
            collection: Name of the collection.
            keys: List of tuples (field, direction) to specify index keys and direction (ex. [("field1", ASCENDING), ("field2", DESCENDING)])
            unique: Enforce index unique

        Returns: The name of the created index.
        """
        return self.db[collection].create_index(keys, unique=unique)
