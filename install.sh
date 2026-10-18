#!/usr/bin/env bash
# ==============================================================================
# JARVIS Mark-LV : One-Line Cross-Platform Installer for Linux & macOS
# ==============================================================================
set -e

REPO_URL="https://github.com/Romjan2000/JARVIS-Mark-LV.git"
INSTALL_DIR="${HOME}/JARVIS-Mark-LV"

echo ""
echo "=========================================================="
echo "   JARVIS MARK-LV : ONE-CLICK CROSS-PLATFORM INSTALLER    "
echo "=========================================================="
echo ""

# 1. Determine target directory
if [ -f "./main.py" ] && [ -f "./setup.py" ]; then
    WORKSPACE_DIR="$(pwd)"
    echo "[✓] Running inside existing JARVIS directory: ${WORKSPACE_DIR}"
else
    WORKSPACE_DIR="${INSTALL_DIR}"
    if ! command -v git &>/dev/null; then
        echo "[!] Git is required but not installed. Please install git and re-run."
        exit 1
    fi

    if [ ! -d "${WORKSPACE_DIR}" ]; then
        echo "[*] Cloning JARVIS Mark-LV repository to ${WORKSPACE_DIR}..."
        git clone "${REPO_URL}" "${WORKSPACE_DIR}"
    fi
fi

cd "${WORKSPACE_DIR}"

# 2. Find Python 3.11, 3.12, or 3.13
PYTHON_BIN=""
for cand in python3.12 python3.11 python3.13 python3 python; do
    if command -v "$cand" &>/dev/null; then
        ver=$("$cand" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || true)
        if [[ "$ver" =~ ^3\.(11|12|13) ]]; then
            PYTHON_BIN="$cand"
            echo "[✓] Found supported Python (${ver}) via: ${PYTHON_BIN}"
            break
        fi
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[!] Compatible Python (3.11, 3.12, or 3.13) was not found."
    echo "    Please install Python 3.11+ using your package manager or python.org."
    exit 1
fi

# 3. Create virtual environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating isolated virtual environment in .venv..."
    "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate

# 4. Upgrade pip and run setup
echo "[*] Upgrading pip..."
pip install --upgrade pip --quiet

echo "[*] Running JARVIS setup..."
python setup.py

chmod +x run_jarvis.sh 2>/dev/null || true

echo ""
echo "=========================================================="
echo "   [✓] JARVIS MARK-LV SETUP FINISHED SUCCESSFULLY!        "
echo "=========================================================="
echo ""
echo "To launch JARVIS:"
echo "  cd \"${WORKSPACE_DIR}\""
echo "  source .venv/bin/activate && python main.py"
echo ""

if [ "$1" != "--no-launch" ]; then
    echo "[*] Launching JARVIS Mark-LV..."
    python main.py
fi
