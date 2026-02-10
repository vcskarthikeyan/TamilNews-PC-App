# Tamil News Dashboard - Complete Setup Guide

![Tamil News Dashboard](https://img.shields.io/badge/Tamil-News-blue) ![Python](https://img.shields.io/badge/Python-3.7+-green) ![Flask](https://img.shields.io/badge/Flask-2.3+-red)

A real-time Tamil news aggregator that scrapes 10+ Tamil newspapers and presents them in a clean, organized dashboard.

---

## 🚀 Quick Start

### Windows
1. **Download** all files to a folder
2. **Double-click** `SETUP_AND_START.bat`
3. **Wait** for dependencies to install
4. **Open** http://localhost:5000 in your browser

### Linux / Mac
1. **Download** all files to a folder
2. **Open Terminal** in that folder
3. **Run:** `bash SETUP_AND_START.sh`
4. **Open** http://localhost:5000 in your browser

---

## 📋 Prerequisites

### All Platforms
- **Python 3.7 or higher**
- **Internet connection** (for scraping news)
- **Web browser** (Chrome, Firefox, Safari, Edge)

### Installation Links
- **Windows:** https://www.python.org/downloads/
  - ⚠️ Check "Add Python to PATH" during installation
- **macOS:** `brew install python3` (if Homebrew installed)
- **Ubuntu/Debian:** `sudo apt install python3 python3-pip`
- **Fedora/RHEL:** `sudo dnf install python3 python3-pip`

---

## 📁 Project Files

```
tamil-news-dashboard/
├── tamil_news_server_final.py       ← Main server
├── tamil-news-dashboard-final.html  ← User interface
├── requirements.txt                 ← Python dependencies
├── SETUP_AND_START.bat              ← Windows quick-start ⭐
├── SETUP_AND_START.sh               ← Linux/Mac quick-start ⭐
├── START.bat                        ← Windows (if already setup)
├── start.sh                         ← Linux/Mac (if already setup)
├── README.md                        ← This file
├── PROJECT_REQUIREMENTS.md          ← Complete requirements doc
├── user_newspapers.json             ← Your selection (auto-created)
├── news_live.json                   ← Current news (auto-created)
└── news_temp.json                   ← Background buffer (auto-created)
```

---

## 🔧 Manual Setup (If Scripts Don't Work)

### Step 1: Install Dependencies

**Windows:**
```batch
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip3 install -r requirements.txt --break-system-packages
```

**If that fails, try with virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Start Server

**Windows:**
```batch
python tamil_news_server_final.py
```

**Linux/Mac:**
```bash
python3 tamil_news_server_final.py
```

### Step 3: Open Browser
Navigate to: **http://localhost:5000**

---

## 🎯 How to Use

### First Time
1. **Wait 2-3 minutes** for initial scraping to complete
2. News will appear automatically
3. Click **📰 Newspapers** button to select which papers to read
4. Your selection is **saved automatically**

### Daily Use
1. **Launch** the script (server starts)
2. **Open** http://localhost:5000
3. **Read** news with expandable content
4. Server **auto-refreshes** every 15 minutes
5. **Click 🔄 Refresh Now** for immediate updates

### Features
- **📰 Newspaper Picker:** Select which newspapers to display
- **🔥 Trending:** High-engagement stories highlighted
- **▼ Expand:** Click arrow to read full article preview (200 words max)
- **🔗 Source Link:** Click headline to read full article on source website
- **⏱️ Auto-Refresh:** Updates every 15 minutes automatically
- **💾 Persistent Selection:** Your choices are remembered

---

## 📰 Available Newspapers

### Default (Priority Order)
1. **Dinamalar** (தினமலர்)
2. **Daily Thanthi** (தினத்தந்தி)
3. **The Hindu Tamil** (தி இந்து தமிழ்)
4. **BBC Tamil** (பிபிசி தமிழ்)
5. **Anandha Vikatan** (ஆனந்த விகடன்)
6. **Kumudham** (குமுதம்)
7. **Dinamani** (தினமணி)
8. **Kaalai Kadhir** (காலை கதிர்)
9. **Dinakaran** (தினகரன்)
10. **Maalai Murasu** (மாலை முரசு)

### Additional (Available in picker)
- Maalai Malar (மாலைமலர்)
- Thinaboomi (தினபூமி)
- Viduthalai (விடுதலை)
- Dinasudar (தினசுடர்)

---

## ❓ Troubleshooting

### "Python is not recognized"
**Cause:** Python not in PATH  
**Fix:** 
- Windows: Reinstall Python and check "Add Python to PATH"
- Linux/Mac: Use `python3` instead of `python`

### "Permission denied" (Linux/Mac)
**Cause:** Script not executable  
**Fix:**
```bash
chmod +x SETUP_AND_START.sh
bash SETUP_AND_START.sh
```

### "pip install failed"
**Cause:** Missing pip or permission issues  
**Fix:**
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### "No news showing"
**Cause:** Initial scrape still running  
**Fix:** Wait 2-3 minutes, then refresh browser

### "Port 5000 already in use"
**Cause:** Another app using port 5000  
**Fix:** 
1. Stop the other app
2. Or edit `tamil_news_server_final.py` line 618:
   - Change `port=5000` to `port=5001`

### "Connection refused"
**Cause:** Server not running or crashed  
**Fix:**
1. Check terminal for error messages
2. Restart the script
3. Check Python version (must be 3.7+)

### Newspaper selection not saving
**Cause:** File write permission  
**Fix:**
```bash
# Check if file exists and is writable
ls -la user_newspapers.json
chmod 644 user_newspapers.json
```

---

## 🛠️ Advanced Configuration

### Change Refresh Interval
Edit `tamil_news_server_final.py`, line ~518:
```python
time.sleep(13 * 60)  # Change 13 to desired minutes
```

### Change Port
Edit `tamil_news_server_final.py`, line ~618:
```python
app.run(host='0.0.0.0', port=5000, ...)  # Change 5000
```

### Add More Newspapers
Edit `tamil_news_server_final.py`, add to `NEWSPAPERS` dict around line 67:
```python
'your_paper': {
    'url': 'https://www.example.com/',
    'tamil': 'உங்கள் செய்தி',
    'english': 'Your Paper',
    'sections': ['https://www.example.com/news/']
}
```

---

## 🔒 Security Notes

- **Local only:** Server binds to localhost by default
- **No authentication:** Designed for personal use
- **Public data only:** Scrapes publicly available news
- **No sensitive info:** Does not collect personal data

---

## 📊 Performance

- **Initial scrape:** 2-3 minutes (10 newspapers)
- **Auto-refresh:** Instant (pre-scraped)
- **Manual refresh:** 2-3 minutes (fresh scrape)
- **Memory usage:** <100MB typical
- **CPU usage:** Low (idle between scrapes)

---

## 🐛 Known Issues

1. **Some articles have no content:** Some sites block scraping or have unusual layouts
2. **Timestamps may be inaccurate:** If site doesn't provide proper metadata
3. **Occasional timeout errors:** Network issues or site downtime (scraper continues)

---

## 📝 License

This is a personal project. Use at your own discretion.  
Respect the terms of service of the news websites being scraped.

---

## 🆘 Support

If you encounter issues:

1. **Read troubleshooting section** above
2. **Check terminal output** for error messages
3. **Ensure Python 3.7+** is installed
4. **Check internet connection**
5. **Try restarting** the script

---

## 🎉 Enjoy Your Tamil News Dashboard!

**Last Updated:** February 5, 2026  
**Version:** 1.0 Final
