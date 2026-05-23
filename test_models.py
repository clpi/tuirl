import unittest
from peewee import SqliteDatabase, IntegrityError

# Import models
from src.models import BaseModel, SSHKey, GPGKey, Database, init_db, db as main_db

# Use an in-memory database for testing
test_db = SqliteDatabase(':memory:')

class TestModels(unittest.TestCase):
    def setUp(self):
        # Bind the models to the test database
        self.models = [SSHKey, GPGKey, Database]
        test_db.bind(self.models, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(self.models)

    def tearDown(self):
        # Drop tables and close the connection
        test_db.drop_tables(self.models)
        test_db.close()
        # Bind back to the main database to prevent state leakage
        main_db.bind(self.models, bind_refs=False, bind_backrefs=False)


    def test_ssh_key_creation(self):
        """Test successful creation of an SSHKey model with default port."""
        key = SSHKey.create(
            name="test_ssh",
            host="example.com",
            user="testuser"
        )
        self.assertEqual(key.name, "test_ssh")
        self.assertEqual(key.port, 22) # Default value
        self.assertIsNone(key.identity_file)

    def test_ssh_key_unique_name(self):
        """Test that SSHKey name must be unique."""
        SSHKey.create(name="test_ssh", host="example.com", user="testuser")
        with self.assertRaises(IntegrityError):
            SSHKey.create(name="test_ssh", host="another.com", user="other")

    def test_gpg_key_creation(self):
        """Test successful creation of a GPGKey model."""
        key = GPGKey.create(
            name="test_gpg",
            key_id="ABCDEF123456",
            email="test@example.com",
            description="A test GPG key"
        )
        self.assertEqual(key.name, "test_gpg")
        self.assertEqual(key.key_id, "ABCDEF123456")

    def test_database_creation(self):
        """Test successful creation of a Database model."""
        db_model = Database.create(
            name="test_db_conn",
            type="postgres",
            host="localhost",
            port=5432,
            user="postgres",
            db_name="test_database"
        )
        self.assertEqual(db_model.name, "test_db_conn")
        self.assertEqual(db_model.port, 5432)


class TestDatabaseInitialization(unittest.TestCase):
    def test_init_db(self):
        """Test that init_db function creates the tables in the database."""
        from unittest.mock import patch
        import src.models as models

        # Test init_db by mocking db.connect, db.create_tables, and db.close
        # to ensure they are called correctly instead of actually running them
        # on a real or in-memory database, which is tricky because Peewee
        # models resolve their connection at class definition time.

        with patch.object(models.db, 'connect') as mock_connect, \
             patch.object(models.db, 'create_tables') as mock_create_tables, \
             patch.object(models.db, 'close') as mock_close:

            models.init_db()

            mock_connect.assert_called_once()
            mock_create_tables.assert_called_once_with([models.SSHKey, models.GPGKey, models.Database], safe=True)
            mock_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
