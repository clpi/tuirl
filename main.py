import sys
from pathlib import Path

# Add the root directory to sys.path so we can import src
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from src.models import init_db
from src.tui import TrackerApp

def main():
    # Initialize the database
    init_db()

    # Run the TUI
    app = TrackerApp()
    app.run()

if __name__ == '__main__':
    main()
