import unittest
from unittest.mock import patch
from src.tui import TrackerApp

class TestMainApplication(unittest.TestCase):
    @patch('src.models.init_db')
    @patch.object(TrackerApp, 'run')
    def test_main(self, mock_run, mock_init):
        import main
        main.main()
        mock_init.assert_called_once()
        mock_run.assert_called_once()
        print("Test passed: init_db and App.run() called correctly")

if __name__ == "__main__":
    unittest.main()
