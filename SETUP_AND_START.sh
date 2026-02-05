#!/bin/bash

# =====================================================
# Tamil News Dashboard - Linux/Mac Setup & Launch
# =====================================================

clear
echo ""
echo "================================================"
echo "  TAMIL NEWS DASHBOARD - SETUP"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ ERROR: Python 3 is not installed!${NC}"
    echo ""
    echo "Please install Python 3.7 or higher:"
    echo ""
    echo "  Ubuntu/Debian:"
    echo "    sudo apt update"
    echo "    sudo apt install python3 python3-pip"
    echo ""
    echo "  macOS (with Homebrew):"
    echo "    brew install python3"
    echo ""
    echo "  Fedora/RHEL:"
    echo "    sudo dnf install python3 python3-pip"
    echo ""
    exit 1
fi

python3 --version
echo -e "${GREEN}✅ Python found${NC}"
echo ""

# Check pip
echo "[2/4] Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  pip3 not found, installing...${NC}"
    python3 -m ensurepip --default-pip
fi
echo -e "${GREEN}✅ pip ready${NC}"
echo ""

# Install dependencies
echo "[3/4] Installing dependencies..."
echo "This may take a minute..."

if pip3 install -q -r requirements.txt --break-system-packages 2>/dev/null; then
    echo -e "${GREEN}✅ All dependencies installed${NC}"
elif pip3 install -q -r requirements.txt; then
    echo -e "${GREEN}✅ All dependencies installed${NC}"
else
    echo -e "${RED}❌ ERROR: Failed to install dependencies${NC}"
    echo ""
    echo "Try running manually:"
    echo "  pip3 install -r requirements.txt --break-system-packages"
    echo ""
    echo "Or create a virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi
echo ""

# Start server
echo "[4/4] Starting server..."
echo ""
echo "================================================"
echo "  SERVER STARTING"
echo "================================================"
echo ""
echo "  URL: http://localhost:5000"
echo "  Port: 5000"
echo ""
echo "  Keep this terminal open while using the dashboard"
echo "  Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

python3 tamil_news_server_final.py

# If server stops
echo ""
echo ""
echo "================================================"
echo "  SERVER STOPPED"
echo "================================================"
echo ""
echo "Press Enter to exit..."
read
