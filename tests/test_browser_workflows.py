import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from actions.browser_workflows import (
    scroll_reels,
    scroll_page,
    youtube_control,
)

class TestBrowserWorkflows(unittest.TestCase):
    def test_scroll_page(self):
        page = MagicMock()
        page.evaluate = AsyncMock()
        
        loop = asyncio.new_event_loop()
        res = loop.run_until_complete(scroll_page(page, "down", 500))
        loop.close()
        
        self.assertIn("Scrolled down", res)
        page.evaluate.assert_called_once()

    def test_scroll_reels(self):
        page = MagicMock()
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        
        loop = asyncio.new_event_loop()
        res = loop.run_until_complete(scroll_reels(page, count=2))
        loop.close()
        
        self.assertIn("Scrolled 2", res)
        self.assertEqual(page.keyboard.press.call_count, 2)

    def test_youtube_control_keys(self):
        page = MagicMock()
        page.keyboard = MagicMock()
        page.keyboard.press = AsyncMock()
        page.evaluate = AsyncMock()
        
        loop = asyncio.new_event_loop()
        res = loop.run_until_complete(youtube_control(page, "fullscreen"))
        loop.close()
        
        self.assertIn("fullscreen", res.lower())
        page.keyboard.press.assert_called_with("f")

if __name__ == "__main__":
    unittest.main()
