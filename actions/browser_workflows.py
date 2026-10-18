"""
actions/browser_workflows.py — High-Level Workflow Automations for Chrome.

Handles real-world user flows with DOM-level precision via Playwright Page:
- YouTube: Search, find video, start playback, toggle play/pause/fullscreen.
- Facebook & Messenger: Search contacts, open chats, type and send messages.
- Social Media: Smoothly scroll feeds, auto-advance Reels, Shorts, and TikToks.
- OS Fallback: Native keyboard and window automation when CDP is inactive.
"""
from __future__ import annotations

import asyncio
import time
from urllib.parse import quote_plus
from typing import Optional

try:
    import pyautogui
    _PYAUTOGUI = True
except ImportError:
    _PYAUTOGUI = False


async def youtube_search_and_play(page, query: str) -> str:
    """
    Searches YouTube, clicks the first organic result, and starts video playback.
    """
    if not query or not query.strip():
        return "Please specify what you want to play on YouTube."

    query = query.strip()
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    
    try:
        print(f"[BrowserWorkflows] Navigating to YouTube search: {query}")
        await page.goto(search_url, wait_until="domcontentloaded", timeout=25_000)
        await asyncio.sleep(1.0)

        # Wait for video titles to render
        selector = "ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title, a#video-title"
        try:
            await page.wait_for_selector(selector, timeout=10_000)
        except Exception:
            pass

        items = page.locator(selector)
        count = await items.count()
        if count == 0:
            return f"No video results found on YouTube for '{query}'."

        first_video = items.first
        title = await first_video.text_content() or query
        title = title.strip()

        print(f"[BrowserWorkflows] Clicking video: {title}")
        await first_video.click()

        # Wait for video element / player
        try:
            await page.wait_for_selector("video, #movie_player", timeout=8_000)
            await asyncio.sleep(0.8)
            # Ensure playback starts
            await page.evaluate("""() => {
                const v = document.querySelector('video');
                if (v && v.paused) {
                    v.play();
                }
            }""")
        except Exception:
            pass

        return f"Now playing on YouTube: '{title}'"

    except Exception as e:
        return f"YouTube error: {e}"


async def youtube_control(page, command: str) -> str:
    """
    Controls YouTube playback (pause, play, mute, fullscreen, next).
    """
    cmd = command.lower().strip()
    try:
        if cmd in ("pause", "play", "toggle"):
            # k or evaluate
            try:
                state = await page.evaluate("""() => {
                    const v = document.querySelector('video');
                    if (!v) return 'No video found';
                    if (v.paused) {
                        v.play();
                        return 'Playing';
                    } else {
                        v.pause();
                        return 'Paused';
                    }
                }""")
                return f"YouTube playback: {state}."
            except Exception:
                await page.keyboard.press("k")
                return f"Toggled YouTube playback."

        elif cmd in ("mute", "unmute"):
            await page.keyboard.press("m")
            return "Toggled YouTube mute."

        elif cmd in ("fullscreen", "full screen", "maximize"):
            await page.keyboard.press("f")
            return "Toggled YouTube fullscreen."

        elif cmd in ("skip", "forward", "forward 10s"):
            await page.keyboard.press("l")
            return "Skipped 10 seconds forward."

        elif cmd in ("rewind", "back", "back 10s"):
            await page.keyboard.press("j")
            return "Rewound 10 seconds."

        elif cmd in ("next", "next video"):
            await page.keyboard.press("Shift+N")
            return "Playing next YouTube video."

        else:
            return f"Unknown YouTube command: '{command}'"

    except Exception as e:
        return f"YouTube control error: {e}"


async def messenger_send_message(page, recipient: str, message: str) -> str:
    """
    Navigates to Messenger / Facebook Messages, finds the recipient, and sends the text.
    """
    if not recipient or not message:
        return "Please specify both a recipient and a message."

    recipient = recipient.strip()
    message = message.strip()

    try:
        # Check current URL
        curr_url = page.url.lower()
        if "messenger.com" not in curr_url and "facebook.com/messages" not in curr_url:
            print("[BrowserWorkflows] Opening Messenger...")
            await page.goto("https://www.messenger.com", wait_until="domcontentloaded", timeout=30_000)
            await asyncio.sleep(2.0)

        # 1. Look for Search input
        search_selectors = [
            "input[placeholder*='Search']",
            "input[aria-label*='Search']",
            "input[type='search']",
            "div[role='combobox'] input",
        ]
        search_box = None
        for sel in search_selectors:
            loc = page.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible():
                search_box = loc.first
                break

        if search_box:
            print(f"[BrowserWorkflows] Searching for contact: {recipient}")
            await search_box.click()
            await search_box.fill(recipient)
            await asyncio.sleep(1.5)
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(0.3)
            await page.keyboard.press("Enter")
            await asyncio.sleep(1.8)
        else:
            print("[BrowserWorkflows] Search box not found, checking existing conversation")

        # 2. Look for Message composition input
        msg_selectors = [
            "div[role='textbox'][aria-label*='Message']",
            "div[role='textbox'][aria-label*='Aa']",
            "div[role='textbox']",
            "div[contenteditable='true']",
            "textarea[name='message_body']",
        ]
        msg_box = None
        for sel in msg_selectors:
            loc = page.locator(sel)
            cnt = await loc.count()
            for i in range(cnt):
                cand = loc.nth(i)
                if await cand.is_visible():
                    msg_box = cand
                    break
            if msg_box:
                break

        if not msg_box:
            return f"Could not find the message input box on Messenger. Is a conversation selected?"

        print(f"[BrowserWorkflows] Typing message to {recipient}...")
        await msg_box.click()
        await msg_box.fill(message)
        await asyncio.sleep(0.4)
        await page.keyboard.press("Enter")
        await asyncio.sleep(0.5)

        return f"Message sent to {recipient} on Messenger: '{message}'"

    except Exception as e:
        return f"Messenger error: {e}"


async def scroll_reels(page, count: int = 1) -> str:
    """
    Scrolls down to the next Reel, Short, or TikTok video.
    """
    count = max(1, min(count, 20))
    try:
        for i in range(count):
            # Most short video players advance on Down Arrow or PageDown
            await page.keyboard.press("ArrowDown")
            await asyncio.sleep(0.4)
            # Mouse wheel fallback
            try:
                await page.mouse.wheel(0, 800)
            except Exception:
                pass
            if i < count - 1:
                await asyncio.sleep(0.5)

        return f"Scrolled {count} reel(s) forward."
    except Exception as e:
        return f"Error scrolling reels: {e}"


async def scroll_page(page, direction: str = "down", amount: int = 600) -> str:
    """
    Smoothly scrolls the current web page.
    """
    dir_clean = direction.lower().strip()
    delta = amount if dir_clean in ("down", "bottom") else -amount
    try:
        await page.evaluate(f"window.scrollBy({{ top: {delta}, behavior: 'smooth' }});")
        await asyncio.sleep(0.3)
        return f"Scrolled {dir_clean} by {amount}px."
    except Exception as e:
        return f"Scroll error: {e}"


# --- OS Fallback for when CDP is not active ---

def os_fallback_browser_action(action: str, **kwargs) -> str:
    """
    Executes browser actions via native OS keystrokes if Chrome is open without CDP.
    """
    if not _PYAUTOGUI:
        return "PyAutoGUI is not installed for OS fallback."

    import pygetwindow as gw
    chrome_windows = [w for w in gw.getWindowsWithTitle("Chrome") if w.visible]
    if not chrome_windows:
        return "No visible Chrome window found to control."

    win = chrome_windows[0]
    try:
        win.activate()
        time.sleep(0.3)
    except Exception:
        pass

    act = action.lower().strip()
    if act == "new_tab":
        pyautogui.hotkey("ctrl", "t")
        url = kwargs.get("url", "")
        if url:
            time.sleep(0.2)
            pyautogui.write(url, interval=0.02)
            pyautogui.press("enter")
        return "Opened new tab via OS shortcut."

    elif act == "close_tab":
        pyautogui.hotkey("ctrl", "w")
        return "Closed tab via OS shortcut."

    elif act == "switch_tab":
        pyautogui.hotkey("ctrl", "tab")
        return "Switched tab via OS shortcut."

    elif act in ("scroll", "scroll_page"):
        direction = kwargs.get("direction", "down")
        amt = kwargs.get("amount", 500)
        clicks = -(amt // 100) if direction == "down" else (amt // 100)
        pyautogui.scroll(clicks)
        return f"Scrolled {direction} via OS."

    elif act == "scroll_reels":
        pyautogui.press("down")
        return "Scrolled reel via OS Down arrow."

    elif act == "search":
        query = kwargs.get("query", "")
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.2)
        pyautogui.write(query, interval=0.02)
        pyautogui.press("enter")
        return f"Searched for '{query}' in Chrome address bar."

    return f"OS fallback not implemented for action: {action}"
