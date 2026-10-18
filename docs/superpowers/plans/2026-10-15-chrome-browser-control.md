# Chrome Browser Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect JARVIS to the user's real Google Chrome browser on Windows via Chrome DevTools Protocol (CDP) and native window automation, providing full tab control, DOM element interaction, YouTube search & play, Messenger messaging, and social feed / Reels scrolling.

**Architecture:** A dual-engine browser control architecture:
1. Primary Engine: Playwright CDP attachment to `http://localhost:9222` to inspect and drive the user's live Chrome browser, active tabs, and logged-in sessions (Google, Facebook, YouTube, Messenger) with 0 profile locking conflicts.
2. Workflow Engine: High-level DOM automation workflows for YouTube (search & play), Messenger (find contact, type message, send), and Reels/Shorts (auto-scroll/advance).
3. Fallback Engine: Windows window focus and keyboard shortcuts (`Ctrl+T`, `Ctrl+W`, `Ctrl+L`, `PageDown`) when Chrome is not launched with the debugging port.
4. Autonomous Agent: `browser-use` configured with `cdp_url` for arbitrary complex multi-step web browsing.

**Tech Stack:** Python 3.12, Playwright, Chrome DevTools Protocol (CDP), `browser-use`, PyAutoGUI, PyGetWindow.

**Spec:** [browser_control_scout_report.md](file:///C:/Users/Tanvir-Khan/.gemini/antigravity-ide/brain/a8fa4e1a-dbc6-45ca-891b-73ad333d4f21/browser_control_scout_report.md)

## Global Constraints
- Must run on Windows 10/11 with Google Chrome.
- Must preserve user cookies, login sessions, and extensions (Google, Facebook, YouTube, Messenger).
- Must avoid console encoding errors on Windows cp1252 (`errors="replace"` or ASCII-safe logging).
- Must fail gracefully if Chrome is closed or if the remote debugging port is not open.

## Review Focus
1. Chrome running without port 9222: Provide instant one-click launcher and fallback to OS shortcuts without crashing.
2. YouTube ads/popups: Gracefully wait for player and skip or click through if needed.
3. Messenger chat finding: Handle dynamic React DOM classes by using semantic aria-labels and placeholder attributes.
4. Multiple tabs: Track open tabs and allow switching or bringing target tab to front.
5. Windows process locks: Do not attempt to lock `AppData\Local\Google\Chrome\User Data` with `launch_persistent_context` when Chrome is active.

---

### Task 1: Chrome Launcher & CDP Detector Helper
**Files:**
- Create: `tools/chrome_launcher.py`
- Create: `tools/launch_chrome_debug.bat`
- Test: `tests/test_chrome_launcher.py`

**Interfaces:**
- Produces: `is_cdp_available(port: int = 9222) -> bool`
- Produces: `launch_chrome_with_cdp(port: int = 9222) -> bool`
- Produces: `get_cdp_version_info(port: int = 9222) -> dict`

- [ ] **Step 1: Write test for CDP detection and launch helpers**
- [ ] **Step 2: Run test to verify initial state**
- [ ] **Step 3: Implement `is_cdp_available`, `launch_chrome_with_cdp`, and `get_cdp_version_info`**
- [ ] **Step 4: Create `tools/launch_chrome_debug.bat` for easy 1-click user startup**
- [ ] **Step 5: Verify tests pass**

---

### Task 2: Playwright CDP Attachment & Tab Management in `actions/browser_control.py`
**Files:**
- Modify: `actions/browser_control.py`
- Test: `tests/test_browser_cdp.py`

**Interfaces:**
- Consumes: `is_cdp_available` from `tools/chrome_launcher.py`
- Produces: `_BrowserSession.connect_cdp() -> bool`
- Produces: `list_tabs() -> list[dict]`
- Produces: `switch_tab(target: str | int) -> str`
- Produces: `new_tab(url: str) -> str`
- Produces: `close_tab(index: int | None) -> str`

- [ ] **Step 1: Write unit tests for CDP connection and tab switching logic**
- [ ] **Step 2: Implement CDP connection in `_BrowserSession._launch`**
- [ ] **Step 3: Update `go_to`, `new_tab`, `close_tab`, and `search` to operate on the real connected Chrome tab**
- [ ] **Step 4: Add `list_tabs` and `switch_tab` actions to `browser_control` entrypoint**
- [ ] **Step 5: Run tests and verify tab actions pass**

---

### Task 3: Dedicated High-Level Workflows (`actions/browser_workflows.py`)
**Files:**
- Create: `actions/browser_workflows.py`
- Modify: `actions/browser_control.py` (route high-level actions)
- Test: `tests/test_browser_workflows.py`

**Interfaces:**
- Consumes: Playwright Page / CDP session from `actions/browser_control.py`
- Produces: `youtube_search_and_play(page, query: str) -> str`
- Produces: `youtube_control(page, command: str) -> str`
- Produces: `messenger_send_message(page, recipient: str, message: str) -> str`
- Produces: `scroll_reels(page, count: int = 1) -> str`
- Produces: `scroll_page(page, direction: str, amount: int) -> str`

- [ ] **Step 1: Write tests for YouTube, Messenger, and Reels workflows**
- [ ] **Step 2: Implement YouTube search, top video click, and playback start**
- [ ] **Step 3: Implement Messenger recipient search, chat selection, and message dispatch**
- [ ] **Step 4: Implement Reels and Shorts scroll down / auto-advance**
- [ ] **Step 5: Wire workflows into `browser_control.py` dispatcher**
- [ ] **Step 6: Run tests and verify workflows pass**

---

### Task 4: Upgrade `actions/browser_agent.py` to use Real Profile via CDP
**Files:**
- Modify: `actions/browser_agent.py`
- Test: `tests/test_browser_agent.py`

**Interfaces:**
- Consumes: `is_cdp_available` from `tools/chrome_launcher.py`
- Produces: `_execute_agent_task(task: str)` connecting via `BrowserProfile(cdp_url="http://localhost:9222")` when CDP is active.

- [ ] **Step 1: Update `BrowserProfile` initialization in `actions/browser_agent.py` to check for active CDP port**
- [ ] **Step 2: Add fallback handling if CDP is not available**
- [ ] **Step 3: Verify autonomous browsing runs through active Chrome**

---

### Task 5: Integration, End-to-End Verification & User Documentation
**Files:**
- Test: End-to-end dry run and live testing
- Create: `docs/CHROME_CONTROL_GUIDE.md`

- [ ] **Step 1: Verify all unit and integration tests pass**
- [ ] **Step 2: Test Chrome launcher and CDP connection**
- [ ] **Step 3: Create quick reference guide for user with voice/text command examples**
- [ ] **Step 4: Present completed solution to user**
