# Tamil News Dashboard - Complete Project Requirements

## Project Overview

A real-time Tamil news aggregator that scrapes 10+ Tamil newspapers and presents them in a clean, organized dashboard with the following capabilities:

## Core Requirements

### 1. News Aggregation
- **Source newspapers** (in priority order):
  1. Dinamalar (தினமலர்)
  2. Daily Thanthi (தினத்தந்தி)
  3. The Hindu Tamil (தி இந்து தமிழ்)
  4. BBC Tamil (பிபிசி தமிழ்)
  5. Anandha Vikatan (ஆனந்த விகடன்)
  6. Kumudham (குமுதம்)
  7. Dinamani (தினமணி)
  8. Kaalai Kadhir (காலை கதிர்)
  9. Dinakaran (தினகரன்)
  10. Maalai Murasu (மாலை முரசு)

- **Additional newspapers** (optional, available in picker):
  - Maalai Malar (மாலைமலர்)
  - Thinaboomi (தினபூமி)
  - Viduthalai (விடுதலை)
  - Dinasudar (தினசுடர்)

### 2. Scraping Strategy
- **Two-pass scraping system:**
  - **Pass 1:** Collect ALL headlines from newspaper homepage
    - No URL path filtering (catches all headline types)
    - Identifies headlines by Tamil text content (18-400 chars with 3+ Tamil characters)
    - Filters out navigation/chrome elements
    - Preserves homepage order (editorial prominence)
  
  - **Pass 2:** Visit top 50 articles for full content
    - Extract article body text (minimum 50 characters)
    - Extract publish timestamp from metadata
    - Calculate trending score based on engagement keywords
    - Cap displayed content at 200 words
    - Add remaining headlines (51+) as headline-only entries

- **Generic topic filtering:**
  - Skip compilation articles (ஒரு பார்வை, தொகுப்பு, overview)
  - Skip editorial/opinion pieces
  - Skip galleries, videos, year-in-review articles
  - Focus on actual news events

- **Refresh mechanism:**
  - Background scraping every 15 minutes
  - Server-owned (works even when browser closed)
  - Scrape at minute 13, swap files at minute 15
  - Aggressive cache-busting for truly fresh content
  - Manual refresh button for immediate updates

### 3. Content Organization
- **Grouping:** Articles grouped by newspaper (priority order)
- **Within each newspaper:**
  - Trending articles first (🔥 badge)
  - Then regular headlines by publish time (newest first)
- **Deduplication:** By URL and similar title text
- **Numbering:** Sequential across all articles (1, 2, 3...)

### 4. Trending Detection
- **Engagement keywords:** மரணம், கொலை, விபத்து, கைது, அறிவிப்பு, etc. (+25 points each)
- **Breaking news indicators:** Class names or text with "trending", "breaking", "முக்கியம்" (+120 points)
- **Visual highlight:** Red gradient circle + 🔥 badge

### 5. User Interface
- **Newspaper selection:**
  - Checkbox picker with all available newspapers
  - Selection persisted to `user_newspapers.json`
  - Never resets (survives browser close, server restart)
  - Changes trigger immediate re-scrape
  - Select All / Clear All buttons

- **News display:**
  - Numbered colored circles (purple for regular, red for trending)
  - Source pill (Tamil + English names)
  - Publish time (formatted: 2:30 PM, Feb 04)
  - Trending badge for high-engagement stories
  - Expandable content section (▼/▲ button)
  - Direct link to original article

- **Header controls:**
  - Live countdown timer (15:00 → 0:00)
  - Status badge (Ready / Fetching / Error)
  - Manual refresh button
  - Newspaper picker button
  - Article count pill (Total / Trending / Headlines)

- **Responsive design:**
  - Desktop: Full layout
  - Mobile: Stacked layout, smaller circles

### 6. Technical Requirements

#### Backend (Python/Flask)
- **Framework:** Flask with CORS
- **Scraping:** requests + BeautifulSoup4
- **Concurrency:** ThreadPoolExecutor (5 workers for newspapers, 4 for articles)
- **Date parsing:** python-dateutil (optional, better timestamp extraction)
- **Background tasks:** Threading daemon for 15-min cycle
- **File storage:** JSON files for news cache and user preferences
- **Port:** 5000 (configurable)

#### Frontend (HTML/CSS/JavaScript)
- **Pure vanilla JS** (no frameworks)
- **CSS animations** for smooth transitions
- **Fetch API** for AJAX calls
- **LocalStorage-free** (all state on server)
- **Status polling** every 5 seconds to detect file swaps

### 7. File Structure
```
tamil-news-dashboard/
├── tamil_news_server_final.py       # Main server (655 lines)
├── tamil-news-dashboard-final.html  # UI (481 lines)
├── requirements.txt                 # Python dependencies
├── README.md                        # Setup guide
├── PROJECT_REQUIREMENTS.md          # This file
├── START.bat                        # Windows quick-start
├── start.sh                         # Linux/Mac quick-start
├── user_newspapers.json             # Selection (auto-created)
├── news_live.json                   # Current feed (auto-created)
└── news_temp.json                   # Background buffer (auto-created)
```

### 8. Data Flow

```
[Homepage Scrape] 
    ↓
[Headline Collection - Pass 1]
    ↓ (top 50)
[Article Visit - Pass 2] → [Content Extraction] → [Timestamp + Trending Score]
    ↓ (51+)
[Headline-Only Entries]
    ↓
[Deduplication (URL + Title)]
    ↓
[Group by Newspaper]
    ↓
[Sort: Trending First, Then Chronological]
    ↓
[Number Sequentially]
    ↓
[JSON File Write]
    ↓
[Browser Polls for File Change]
    ↓
[UI Re-render]
```

### 9. Performance Targets
- **Initial scrape:** 2-3 minutes (10 newspapers, 50 articles each)
- **Auto-refresh:** Instant (pre-scraped data)
- **Manual refresh:** 2-3 minutes (fresh scrape)
- **Memory:** <100MB typical usage
- **Browser:** <20MB, smooth 60fps animations

### 10. Error Handling
- **Network failures:** Skip newspaper, log error, continue
- **Parse errors:** Return empty list, log, continue
- **File write errors:** Keep previous data, log error
- **Empty results:** Display "No news available" message
- **Concurrent access:** Thread locks for state updates

### 11. Cross-Platform Support

#### Windows
- Batch scripts for one-click setup
- Python 3.7+ from Microsoft Store or python.org
- pip install with --break-system-packages not needed

#### Linux/Mac
- Bash scripts with chmod +x
- Python 3.7+ (usually pre-installed)
- pip install with --break-system-packages flag
- Virtual environment support

#### Docker (future)
- Dockerfile for containerized deployment
- docker-compose for easy orchestration

### 12. Security Considerations
- **No authentication** (local-only by default)
- **CORS enabled** (for local development)
- **No sensitive data** (public news only)
- **Rate limiting:** Built into scraper (timeout + delays)
- **User input:** No direct user input to backend (checkbox selection only)

### 13. Customization Points
- Newspaper list and priority order
- Engagement keywords for trending detection
- Content length limits (words, paragraphs)
- Refresh interval (currently 15 minutes)
- Number of articles per newspaper
- UI colors and styling
- Date/time formats

### 14. Known Limitations
- **Single-language:** Tamil only (by design)
- **No search:** Sequential browsing only
- **No history:** Current session only
- **No bookmarks:** Click through to source
- **No offline mode:** Requires active internet
- **No mobile app:** Web-only interface

### 15. Future Enhancements (Not Required)
- Search/filter by keyword
- Category filtering (politics, sports, etc.)
- Multi-language support
- RSS feed generation
- Email digest
- Mobile app (React Native)
- PWA with offline caching
- User accounts and saved preferences
- Article summarization (AI)
- Sentiment analysis

---

## Success Criteria

✅ All specified newspapers scraped successfully  
✅ Real-time refresh every 15 minutes (server-owned)  
✅ Trending articles highlighted correctly  
✅ Articles grouped by newspaper in priority order  
✅ User selection persists across sessions  
✅ Content displays properly (200 word limit)  
✅ Expand/collapse works smoothly  
✅ Cross-platform setup works (Windows/Linux/Mac)  
✅ No artificial limits (all homepage headlines captured)  
✅ Fresh content on every refresh (no stale cache)  

---

**Project Status:** ✅ Complete and Fully Functional  
**Last Updated:** February 5, 2026  
**Version:** 1.0 Final
