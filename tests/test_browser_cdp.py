import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from actions.browser_control import (
    _BrowserSession,
    _normalize_url,
    browser_control,
)

class TestBrowserCDP(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(_normalize_url("youtube.com"), "https://youtube.com")
        self.assertEqual(_normalize_url("facebook"), "https://facebook.com")
        self.assertEqual(_normalize_url("https://google.com"), "https://google.com")

    def test_cdp_connection_flag_in_session(self):
        sess = _BrowserSession("chrome")
        self.assertFalse(sess.is_cdp)

    @patch("actions.browser_control.is_cdp_available", return_value=True)
    def test_browser_control_list_tabs_signature(self, mock_cdp):
        # Verify browser_control accepts list_tabs action
        res = browser_control({"action": "list_tabs", "browser": "chrome"})
        self.assertIsInstance(res, str)

if __name__ == "__main__":
    unittest.main()
