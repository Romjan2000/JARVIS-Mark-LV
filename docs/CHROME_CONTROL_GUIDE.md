# 🚀 JARVIS Chrome Browser Control Guide

JARVIS now has full control over your **real Google Chrome browser** on Windows with zero profile-locking conflicts. You can control tabs, navigate websites, click elements, search YouTube and play videos, message contacts on Messenger, and scroll Facebook / Reels / Shorts.

---

## 1. Quick Start: Connecting JARVIS to Your Chrome

To give JARVIS direct access to your **active tabs and logged-in accounts** (YouTube, Facebook, Messenger, etc.):

### Method A: One-Click Launcher (Recommended)
Simply double-click the included batch script:
```
tools\launch_chrome_debug.bat
```
This starts your normal Google Chrome with remote debugging on port `9222`. All your extensions, bookmarks, history, and logins are 100% active.

### Method B: Ask JARVIS Directly
You can type or speak:
> *"JARVIS, launch my Chrome browser"* or *"JARVIS, connect to Chrome"*

### Method C: Automatic Fallback
Even if you forgot to start Chrome with port `9222`, JARVIS automatically uses **native window automation and hotkeys** so your commands (`Ctrl+T`, `Ctrl+W`, `Ctrl+L`, address bar typing, page scrolling) still work!

---

## 2. Voice & Text Commands You Can Give JARVIS

### 🎬 YouTube Search & Playback
- **Play a video**: *"JARVIS, search for lofi chill beats on YouTube and play it"*
- **Control playback**:
  - *"JARVIS, pause the video"* / *"JARVIS, play"*
  - *"JARVIS, mute YouTube"* / *"unmute"*
  - *"JARVIS, make YouTube fullscreen"*
  - *"JARVIS, skip 10 seconds"*
  - *"JARVIS, play the next video"*

### 💬 Facebook & Messenger
- **Send a message**:
  - *"JARVIS, send a message to Tanvir on Messenger saying Hello, how are you?"*
  - *"JARVIS, message John on Facebook saying I will be there in 10 minutes"*
- JARVIS opens Messenger, locates the conversation, types into the message box, and presses Enter.

### 📱 Reels, Shorts & Feed Scrolling
- **Reels & Shorts**:
  - *"JARVIS, scroll reel"* or *"JARVIS, next reel"* (advances video)
  - *"JARVIS, scroll 3 reels forward"*
- **Page Scrolling**:
  - *"JARVIS, scroll down"*
  - *"JARVIS, scroll up 800 pixels"*
  - *"JARVIS, scroll Facebook"*

### 📑 Tab & Navigation Control
- **Open new tab**: *"JARVIS, open a new tab"* or *"JARVIS, open new tab to wikipedia.org"*
- **List open tabs**: *"JARVIS, list all my open tabs in Chrome"*
- **Switch tabs**: *"JARVIS, switch to the YouTube tab"* or *"JARVIS, switch to tab 2"*
- **Close tabs**: *"JARVIS, close this tab"* or *"JARVIS, close tab 3"*
- **Address bar search**: *"JARVIS, search for quantum computing on Google"*
- **Navigate directly**: *"JARVIS, go to github.com"*

### 🖱️ Element Interaction on Any Website
- **Click**: *"JARVIS, click the sign in button"* or *"JARVIS, click the submit button"*
- **Type**: *"JARVIS, type test@example.com into the email field"*
- **Press Keys**: *"JARVIS, press Enter"* or *"JARVIS, press Escape"*
- **Smart Click**: *"JARVIS, click the blue button on the top right"*

---

## 3. Autonomous Multi-Step Browsing
For complex tasks across arbitrary websites, JARVIS's **BrowserAgent** (`browser-use` + Gemini) also automatically attaches to your live Chrome session via port 9222.
Example:
> *"JARVIS, go to Amazon, find the top-rated wireless keyboard, and tell me the price"*
