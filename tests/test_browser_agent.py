import unittest
from unittest.mock import patch, MagicMock

from tools.chrome_launcher import is_cdp_available

class TestBrowserAgentCDP(unittest.TestCase):
    @patch("actions.browser_agent.is_cdp_available", return_value=True)
    def test_browser_agent_detects_cdp(self, mock_cdp):
        from actions.browser_agent import is_cdp_available
        self.assertTrue(is_cdp_available(9222))

    @patch("actions.browser_agent.is_cdp_available", return_value=False)
    def test_browser_agent_detects_no_cdp(self, mock_cdp):
        from actions.browser_agent import is_cdp_available
        self.assertFalse(is_cdp_available(9222))

if __name__ == "__main__":
    unittest.main()
