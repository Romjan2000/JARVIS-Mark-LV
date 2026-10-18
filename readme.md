# ⚡ JARVIS Mark-LV (Mark-55)

> **The Ultimate Real-Time Autonomous Personal AI Assistant**  
> *Holographic 3D Avatar • Gemini 3.1 Flash Live Engine • Direct Chrome CDP Control • Zero Subscriptions*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg?logo=linux&logoColor=white)](https://github.com/Romjan2000/JARVIS-Mark-LV)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Gemini%203.1%20Flash%20Live-orange.svg?logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-green.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

## ⚡ Single-Line Quick Setup (Run on Any PC)

Set up and launch JARVIS on any PC with a single terminal command:

### 🪟 Windows (PowerShell)
Open PowerShell (as regular user) and run:
```powershell
powershell -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/Romjan2000/JARVIS-Mark-LV/main/install.ps1 | iex"
```

### 🍎 macOS & 🐧 Linux (Terminal)
Open Terminal and run:
```bash
curl -fsSL https://raw.githubusercontent.com/Romjan2000/JARVIS-Mark-LV/main/install.sh | bash
```

---

### 💻 Standard Git One-Liner (Any Platform)
If you already have Git and Python installed:
```bash
git clone https://github.com/Romjan2000/JARVIS-Mark-LV.git && cd JARVIS-Mark-LV && python setup.py && python main.py
```

---

## ✨ What is JARVIS Mark-LV?

**JARVIS Mark-LV** is an intelligent, voice-and-vision-enabled AI desktop companion built upon Google's **Gemini 3.1 Flash Live API**. It listens, sees through your screen/webcam, speaks with natural low-latency voice, and directly controls your computer and browser.

### 🌟 Key Innovations

- **🧑‍🎤 Holographic 3D Avatar:** Fully animated 3D human face geometry (MediaPipe canonical model) rendered entirely in software at 60 FPS — **no dedicated GPU required**.
- **👄 True Multilingual Lip-Sync:** 50+ mouth shapes per second extracted from formant acoustics and phonetic transcripts across English, Bengali, Hindi, Spanish, Cyrillic, and more.
- **🌐 Real Chrome Browser Control (CDP):** Attach directly to your running Google Chrome session via Chrome DevTools Protocol (`localhost:9222`). Interact with active tabs, search YouTube, scroll feeds, and send messages without profile locking.
- **🪜 Resilient 9-Model Ladder:** Automatic fallback across 9 Gemini models with measured response times. Quota exhaustion (429) or timeouts (503/504) dynamically step to the next rung without hanging.
- **🧠 Recallable Memory & Undo:** Infinite-context local memory stored in `memory/long_term.json`. Undo reversible system actions (`"undo that"`) with full state tracking.
- **🎙️ Local Offline Wake Word:** Zero-cloud wake word detection for **"Hey Jarvis"** using openWakeWord.
- **📺 In-HUD Video & Media Player:** Plays YouTube and web videos directly inside the holographic HUD where the avatar sits, with automatic mute/sound awareness.
- **🛡️ 100% Private & Autonomous:** All configuration, memory, logs, and TLS credentials stay local on your device. Zero external subscriptions.

---

## 🚀 Core Features Matrix

| Feature | Capability |
|---|---|
| **Real-time Voice** | Ultra-low latency two-way streaming conversation via Gemini Live API |
| **Visual Awareness** | Live webcam feed & desktop screen capture piped directly to the visual engine |
| **Browser Control** | Chrome CDP integration, tab navigation, YouTube search/play, Facebook/Messenger workflows |
| **System Automation** | App launcher, audio volume, display brightness, WiFi management, task scheduler |
| **Push-to-Talk** | Global hotkey (`Ctrl + Space`) with self-calibrating echo cancellation |
| **Hardware Telemetry** | Live monitoring of CPU, RAM, GPU temperature, and battery levels |
| **Web Research** | Grounded dual-engine search (Google Gemini Grounding + DuckDuckGo fallback) |
| **Undo Engine** | Reverse file moves, renames, writes, and setting modifications on voice demand |
| **Smart Confirmation** | Irreversible commands (shutdown, reboot, WiFi toggle) require manual HUD confirmation |
| **Audio Device Selector** | Dynamic device picker calibrated to host OS APIs (DirectSound, MME, CoreAudio, ALSA) |
| **Plugin Extensibility** | Drop any custom `.py` file into `plugins/` to immediately register new capabilities |

---

## 📋 System Requirements

| Component | Minimum Requirement | Recommended |
|---|---|---|
| **Operating System** | Windows 10/11 (64-bit), macOS 12+, or modern Linux | Windows 11 (64-bit) |
| **Python** | Python 3.11, 3.12, or 3.13 | Python 3.12 |
| **Microphone** | Any functional microphone or headset | USB / Headset microphone |
| **Speakers** | Built-in or external speakers / headphones | Low-latency headphones |
| **GPU** | **None required** (Software rendering) | Any standard GPU |
| **Google API Key** | Free Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey) | Free Tier / Pay-as-you-go |
| **Web Browser** | Google Chrome (for advanced CDP browser control) | Google Chrome latest |

---

## 🛠️ Step-by-Step Manual Installation

If you prefer installing manually step-by-step instead of using the one-line setup command:

### 1. Clone the Repository
```bash
git clone https://github.com/Romjan2000/JARVIS-Mark-LV.git
cd JARVIS-Mark-LV
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Run Automated Dependency Setup
```bash
python setup.py
```
> `setup.py` automatically detects your operating system and filters out OS-specific packages (e.g. Windows pywin32 vs Linux system tools), installs Playwright browsers, and verifies 3D assets.

### 4. Launch JARVIS
```bash
# Windows (via batch script or python)
run_jarvis.bat
# or:
python main.py

# Linux / macOS
./run_jarvis.sh
# or:
python3 main.py
```

---

## 🔑 First-Time Configuration

1. **Obtain your Free Gemini API Key:**
   - Head over to [Google AI Studio](https://aistudio.google.com/app/apikey).
   - Click **Create API Key**.
2. **Enter Key on First Launch:**
   - When JARVIS starts for the first time, an intuitive setup window will appear.
   - Paste your API key, choose your preferred assistant voice, HUD accent color, and your name.
   - Your key is safely saved locally in `config/api_keys.json` (which is git-ignored and never leaves your PC).

---

## 🌐 Google Chrome CDP Integration

JARVIS Mark-LV features a dedicated **Chrome DevTools Protocol (CDP)** bridge that lets JARVIS drive your real, logged-in Google Chrome browser.

### Starting Chrome with Debugging Port
To enable JARVIS to interact with your active tabs and logged-in sessions:

- **Windows:** Double click `tools/launch_chrome_debug.bat`  
  *(or start Chrome from terminal with `chrome.exe --remote-debugging-port=9222`)*
- **macOS:**
  ```bash
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
  ```
- **Linux:**
  ```bash
  google-chrome --remote-debugging-port=9222
  ```

### Voice Commands for Chrome
- *"Search YouTube for interstellar soundtrack and play it"*
- *"Open a new tab and search for latest AI news"*
- *"Switch to the Messenger tab and message Alex"*
- *"Scroll down on this page"*
- *"Close the current tab"*

---

## 🎙️ Common Voice Commands

| Category | Example Commands |
|---|---|
| **Conversational** | *"Good morning Jarvis"*, *"Tell me about quantum computing"* |
| **Media & YouTube** | *"Play the new Dune trailer on HUD"*, *"Mute the video"*, *"Pause"* |
| **PC Control** | *"Open Spotify"*, *"Set volume to 40%"*, *"Turn on dark mode"* |
| **Files & Folders** | *"Organize my desktop"*, *"What files are in my Downloads folder?"* |
| **Undo** | *"Undo that"*, *"Put the files back"* |
| **Vision** | *"Look at my screen, what error is showing?"*, *"What am I holding in the camera?"* |
| **Memory** | *"Remember that my car keys are on the kitchen counter"*, *"Where are my keys?"* |
| **System Info** | *"Check CPU and RAM usage"*, *"What is the weather in Dhaka?"* |

---

## 📁 Repository Architecture

```
JARVIS-Mark-LV/
├── main.py                   # Core event loop — Gemini Live WebSocket, audio I/O & tool dispatcher
├── ui.py                     # PyQt6 Holographic HUD — 3D avatar canvas, waveform & drawer
├── setup.py                  # OS-aware intelligent installer & Playwright browser provisioning
├── install.ps1               # One-line automated bootstrap installer for Windows
├── install.sh                # One-line automated bootstrap installer for Linux & macOS
├── run_jarvis.bat            # Windows 1-click launcher with venv detection
├── run_jarvis.sh             # Unix 1-click launcher
├── requirements.txt          # Python dependencies with OS sys_platform markers
├── .gitignore                # Comprehensive exclusion of secrets, keys, and personal memories
│
├── actions/                  # Modular skill handlers (auto-discovered at boot)
│   ├── browser_control.py    # Chrome CDP and Playwright web automation
│   ├── video_player.py       # In-HUD YouTube & video stream player
│   ├── computer_control.py   # Keyboard shortcuts, mouse and window management
│   ├── computer_settings.py  # Volume, brightness, WiFi, system settings
│   ├── file_controller.py    # Local file management & desktop organizer
│   ├── open_app.py           # Cross-platform application launcher
│   ├── screen_processor.py   # Desktop screen & webcam vision capture
│   ├── system_monitor.py     # CPU, RAM, GPU telemetry
│   └── weather_report.py     # Real-time weather reporting
│
├── core/                     # Internal subsystems
│   ├── gemini.py             # 9-model resilience ladder, timeouts, and cooldown management
│   ├── avatar.py             # 3D software rasterizer & facial lighting engine
│   ├── avatar_mesh.py        # Facial geometry loader and vertex rig builder
│   ├── face_model.obj        # Canonical 468-vertex 3D facial geometry
│   ├── viseme.py             # Real-time audio formant & phonetic lip-sync mapper
│   ├── audio_devices.py      # Host API audio device measurement & selection
│   ├── undo.py               # Reversible action transaction history
│   └── wake_word.py          # Local openWakeWord engine ("Hey Jarvis")
│
├── tools/                    # Chrome debugging helpers & launcher utilities
│   ├── chrome_launcher.py    # CDP detector and connection manager
│   └── launch_chrome_debug.bat # 1-click Chrome launcher with remote debugging port 9222
│
├── memory/                   # Local persistent memory store
│   └── memory_manager.py     # Fast local memory indexing & retrieval
│
└── config/                   # Configuration templates & application assets
    └── jarvis.ico            # Desktop & window icon
```

---

## 🔒 Security & Privacy

- **Zero Data Leakage:** Your Gemini API key (`config/api_keys.json`), private memories (`memory/long_term.json`), and TLS certificates (`config/certs/`) are stored strictly locally and ignored by Git.
- **Safe Execution Gate:** Irreversible commands (such as system shutdown, reboot, or WiFi disconnection) cannot be triggered autonomously by the model — they present a confirmation prompt on the HUD.
- **Audio Privacy:** Audio streaming is only active while the push-to-talk button is held (`Ctrl + Space`) or after the local offline wake word is spoken.

---

## ❓ Troubleshooting & FAQ

<details>
<summary><b>1. "JARVIS can't hear me" or microphone not picking up</b></summary>
Open the settings drawer (⚙ icon) and navigate to <b>🎧 AUDIO DEVICES</b>. JARVIS measures your available microphones and filters out virtual sound mappers. Select your physical microphone by name.
</details>

<details>
<summary><b>2. Chrome Browser Control shows "CDP not connected"</b></summary>
Make sure Google Chrome is running with remote debugging enabled. Run <code>tools/launch_chrome_debug.bat</code> or launch Chrome with <code>--remote-debugging-port=9222</code>.
</details>

<details>
<summary><b>3. Playwright browser error during setup</b></summary>
If automatic browser installation was skipped due to network restrictions, manually install them by running:
<code>python -m playwright install chromium firefox</code>
</details>

<details>
<summary><b>4. Python version compatibility error</b></summary>
JARVIS requires Python 3.11, 3.12, or 3.13. If you have multiple versions of Python installed on Windows, run setup using the specific version launcher:
<code>py -3.12 setup.py</code>
</details>

---

## 📜 License

This project is licensed for **personal and non-commercial use** under the **[Creative Commons BY-NC 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/)**.

---

<p align="center">
  <b>Built with ❤️ by Romjan & the Open Source AI Community</b><br>
  <i>Empowering personal computing with private, autonomous intelligence.</i>
</p>
