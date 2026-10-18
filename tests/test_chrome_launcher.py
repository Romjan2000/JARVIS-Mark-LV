import unittest
import urllib.request
from unittest.mock import patch, MagicMock

from tools.chrome_launcher import (
    is_cdp_available,
    get_cdp_version_info,
    find_chrome_executable,
)

class TestChromeLauncher(unittest.TestCase):
    def test_is_cdp_available_false_when_unreachable(self):
        self.assertFalse(is_cdp_available(port=59999))

    def test_is_cdp_available_true_when_endpoint_responds(self):
        with patch("urllib.request.urlopen") as mock_url:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = b'{"Browser": "Chrome/124.0.0.0"}'
            mock_url.return_value.__enter__.return_value = mock_resp
            self.assertTrue(is_cdp_available(port=9222))

    def test_get_cdp_version_info(self):
        with patch("urllib.request.urlopen") as mock_url:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.read.return_value = b'{"Browser": "Chrome/124.0.0.0", "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/123"}'
            mock_url.return_value.__enter__.return_value = mock_resp
            info = get_cdp_version_info(port=9222)
            self.assertEqual(info.get("Browser"), "Chrome/124.0.0.0")
            self.assertIn("webSocketDebuggerUrl", info)

    def test_find_chrome_executable(self):
        exe = find_chrome_executable()
        self.assertIsNotNone(exe)
        self.assertIn("chrome.exe", exe.lower())

if __name__ == "__main__":
    unittest.main()
