import asyncio
import sys
from pathlib import Path

# Add the root directory to sys.path so we can import src
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from src.models import init_db
from src.tui import TrackerApp

async def main():
    init_db()
    app = TrackerApp()
    async with app.run_test() as pilot:
        # Wait for the app to start and render
        await pilot.pause()

        # Take a screenshot
        svg = app.export_screenshot(title="TrackerApp")
        with open("screenshot.svg", "w") as f:
            f.write(svg)

asyncio.run(main())
