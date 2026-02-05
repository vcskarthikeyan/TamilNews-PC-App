#!/usr/bin/env python3
"""
Tamil News Dashboard – FINAL VERSION
=====================================
• Server owns the 15-min cycle (works with tab closed).
• Two-pass scraper per newspaper (no URL-path filter).
• Newspaper catalogue in exact user-requested priority order.
• User checkbox selection persisted in user_newspapers.json (same dir as this script).
• GET  /api/newspapers   → full catalogue + each paper's selected flag
• POST /api/newspapers   → save new selection
• GET  /api/news?mode=live|fresh  → news feed (only selected papers)
"""

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import random
import threading
import json

try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None

app = Flask(__name__)
CORS(app)

# ─── paths ──────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
MAIN_HTML       = os.path.join(BASE_DIR, 'tamil-news-dashboard-final.html')
TEMP_NEWS       = os.path.join(BASE_DIR, 'news_temp.json')
LIVE_NEWS       = os.path.join(BASE_DIR, 'news_live.json')
USER_PREFS_FILE = os.path.join(BASE_DIR, 'user_newspapers.json')   # ← persisted selection

# ─── shared state ───────────────────────────────────────────────────
STATE = {
    'is_scraping':     False,
    'last_scrape':     None,
    'scrape_progress': '',
}
STATE_LOCK = threading.Lock()

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36',
]

# ─── newspaper catalogue  (ORDER = priority the user asked for) ────
# Python 3.7+ dicts preserve insertion order.  The first 10 keys are
# the user's priority list; the remaining 4 are extras that are
# available in the dropdown but OFF by default.
NEWSPAPERS = {
    # ── priority 1-10  (default ON) ─────────────────────────────────
    'dinamalar': {
        'url':     'https://www.dinamalar.com/',
        'tamil':   'தினமலர்',
        'english': 'Dinamalar',
        'sections': ['https://www.dinamalar.com/news/'],
    },
    'dailythanthi': {
        'url':     'https://www.dailythanthi.com/',
        'tamil':   'தினத்தந்தி',
        'english': 'Daily Thanthi',
        'sections': ['https://www.dailythanthi.com/tamil/'],
    },
    'thehindu': {
        'url':     'https://tamil.thehindu.com/',
        'tamil':   'தி இந்து தமிழ்',
        'english': 'The Hindu Tamil',
        'sections': ['https://tamil.thehindu.com/latest/'],
    },
    'bbc': {
        'url':     'https://www.bbc.com/tamil',
        'tamil':   'பிபிசி தமிழ்',
        'english': 'BBC Tamil',
        'sections': ['https://www.bbc.com/tamil/articles'],
    },
    'anandha_vikatan': {
        'url':     'https://www.anavex.com/',          # primary
        'tamil':   'ஆனந்த விகடன்',
        'english': 'Anandha Vikatan',
        'sections': ['https://www.vikatan.com/news/tamil/'],
    },
    'kumudham': {
        'url':     'https://www.kumudham.com/',
        'tamil':   'குமுதம்',
        'english': 'Kumudham',
        'sections': ['https://www.kumudham.com/news/'],
    },
    'dinamani': {
        'url':     'https://www.dinamani.com/',
        'tamil':   'தினமணி',
        'english': 'Dinamani',
        'sections': ['https://www.dinamani.com/latest-news/'],
    },
    'kaalai_kadhir': {
        'url':     'https://www.kaalaikadhir.com/',
        'tamil':   'காலை கதிர்',
        'english': 'Kaalai Kadhir',
        'sections': [],
    },
    'dinakaran': {
        'url':     'https://www.dinakaran.com/',
        'tamil':   'தினகரன்',
        'english': 'Dinakaran',
        'sections': ['https://www.dinakaran.com/news/'],
    },
    'maalaimurasu': {
        'url':     'https://www.maalaimurasu.com/',
        'tamil':   'மாலை முரச்ச',
        'english': 'Maalai Murasu',
        'sections': [],
    },
    # ── extras  (default OFF) ───────────────────────────────────────
    'maalaimalar': {
        'url':     'https://www.maalaimalar.com/',
        'tamil':   'மாலைமலர்',
        'english': 'Maalai Malar',
        'sections': [],
    },
    'thinaboomi': {
        'url':     'https://www.thinaboomi.com/',
        'tamil':   'தினபூமி',
        'english': 'Thinaboomi',
        'sections': [],
    },
    'viduthalai': {
        'url':     'https://www.viduthalai.in/',
        'tamil':   'விடுதலை',
        'english': 'Viduthalai',
        'sections': [],
    },
    'dinasudar': {
        'url':     'https://www.dinasudar.com/',
        'tamil':   'தினசுடர்',
        'english': 'Dinasudar',
        'sections': [],
    },
}

# Default = first 10 keys (the priority list)
DEFAULT_SELECTED = list(NEWSPAPERS.keys())[:10]

# ─── word lists ─────────────────────────────────────────────────────
GENERIC_SKIP = [
    'ஒரு பார்வை','சிறப்புக் கட்டுரைகள்','சிறப்பு கட்டுரை',
    'தலையங்கம்','செย்தித் தொகுப்பு','தொகுப்பு',
    'புகைப்படங்கள்','வீடியோ','சூழல்','பின்னணி','விளக்கம்',
    'editorial','opinion','compilation','overview',
    'gallery','video','background',
]
ENGAGEMENT_WORDS = [
    'மரணம்','கொலை','விபத்து','பரபர','சம்பவம்','அதிர்ச்சி',
    'வெளியானது','தீர்ப்பு','போராட்டம்','தாக்குதல்','கைது',
    'வழக்கு','நடவடிக்கை','எதிர்ப்பு','பதற்றம்','சிக்கல்',
    'குற்றச்சாట்டு','முடிவு','அறிவிப்பு','வெற்றி','தடக்கம்',
]
NAV_WORDS = [
    'home','menu','login','search','epaper','e-paper','signin',
    'register','signup','subscribe','contact us','about us',
    'terms','privacy','cookie','advertisement','sponsor',
    'careers','help','faq','sitemap',
    'அறிமுகம்','தொடர்பு','சந்தா','கிட்ட மேலும்',
]

# ════════════════════════════════════════════════════════════════════
# USER-PREF FILE  (read / write user_newspapers.json)
# ════════════════════════════════════════════════════════════════════

def _read_selection():
    """Return the persisted list of selected keys.  Falls back to DEFAULT."""
    try:
        with open(USER_PREFS_FILE, 'r', encoding='utf-8') as f:
            sel = json.load(f).get('selected', [])
        valid = [k for k in sel if k in NEWSPAPERS]   # drop stale keys
        return valid if valid else list(DEFAULT_SELECTED)
    except:                                            # file missing / corrupt
        return list(DEFAULT_SELECTED)

def _write_selection(keys):
    """Persist selection atomically."""
    tmp = USER_PREFS_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump({'selected': keys}, f, ensure_ascii=False)
    os.replace(tmp, USER_PREFS_FILE)

# ════════════════════════════════════════════════════════════════════
# UTILITY
# ════════════════════════════════════════════════════════════════════

def _log(msg):
    print(msg, flush=True)
    with STATE_LOCK:
        STATE['scrape_progress'] = msg

def _headers():
    return {
        'User-Agent':      random.choice(USER_AGENTS),
        'Cache-Control':   'no-cache, no-store, must-revalidate',
        'Pragma':          'no-cache',
        'Expires':         '0',
        'Accept-Language': 'ta-IN,ta;q=0.9,en-IN;q=0.8,en;q=0.7',
    }

def _abs_url(base, href):
    href = href.strip()
    if href.startswith('http'):  return href
    if href.startswith('//'):    return 'https:' + href
    from urllib.parse import urlparse
    p = urlparse(base.rstrip('/'))
    if href.startswith('/'):
        return f"{p.scheme}://{p.netloc}{href}"
    return f"{p.scheme}://{p.netloc}/{href}"

def _parse_dt(s):
    if not s: return None
    try:
        s = s.split('+')[0].split('Z')[0]
        dp, tp = (s.split('T') + ['00:00:00'])[:2]
        y, m, d = dp.split('-')
        parts = tp.split(':')
        return datetime(int(y), int(m), int(d),
                        int(parts[0]) if len(parts)>0 else 0,
                        int(parts[1]) if len(parts)>1 else 0,
                        int(float(parts[2])) if len(parts)>2 else 0)
    except:
        return None

# ════════════════════════════════════════════════════════════════════
# HEADLINE CLASSIFIER
# ════════════════════════════════════════════════════════════════════

TAMIL_RE = re.compile(r'[\u0B80-\u0BFF]')

def _looks_like_headline(text, href):
    if not text or not href:                          return False
    if len(text) < 18 or len(text) > 400:            return False
    if len(TAMIL_RE.findall(text)) < 3:              return False
    tl = text.lower()
    if any(w in tl for w in NAV_WORDS):              return False
    if any(g.lower() in tl for g in GENERIC_SKIP):   return False
    if re.search(r'20\d{2}.*பார்வை', text):        return False
    return True

# ════════════════════════════════════════════════════════════════════
# TIMESTAMP  &  CONTENT  EXTRACTION
# ════════════════════════════════════════════════════════════════════

def extract_timestamp(soup, url):
    meta = soup.find('meta', {'property': 'article:published_time'})
    if meta and meta.get('content'):
        ts = _parse_dt(meta['content'])
        if ts: return ts
        if date_parser:
            try:  return date_parser.parse(meta['content'])
            except: pass
    tag = soup.find('time', {'datetime': True})
    if tag:
        ts = _parse_dt(tag['datetime'])
        if ts: return ts
        if date_parser:
            try:  return date_parser.parse(tag['datetime'])
            except: pass
    for t in ('span','div','p'):
        el = soup.find(t, {'class': re.compile(r'time|date|publish|posted|ago', re.I)})
        if el:
            txt = el.get_text(strip=True)
            if txt and date_parser:
                try:  return date_parser.parse(txt, fuzzy=True)
                except: pass
    m = re.search(r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', url)
    if m:
        try: return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except: pass
    return None

def extract_content(soup):
    for tag in soup.find_all(['script','style','nav','header','footer',
                              'iframe','aside','form','noscript']):
        tag.decompose()
    container = (
        soup.find('article') or
        soup.find('div', class_=re.compile(
            r'article-body|story-body|post-content|news-body|'
            r'article-content|entry-content|article-text|'
            r'content-area|main-content|news-detail|StoryContent', re.I)) or
        soup.find('div', id=re.compile(r'article|story|content|detail', re.I))
    )
    paras = container.find_all(['p','div']) if container else soup.find_all('p')
    junk  = ['subscribe','follow us','share this','advertisement','login',
             'register','copyright','all rights','also read',
             'சந்தா','பகிரவும்','விளம்பரம்','இதையும் படியுங்கள்','மேலும் படிக்க']
    texts, seen = [], set()
    for p in paras:
        t = p.get_text(strip=True)
        if len(t) < 25: continue
        if any(j in t.lower() for j in junk): continue
        short = t[:80]
        if short in seen: continue
        seen.add(short); texts.append(t)
    body = '\n\n'.join(texts)
    return body if len(body) >= 50 else None    # lowered from 200 to 50

# ════════════════════════════════════════════════════════════════════
# PER-NEWSPAPER  TWO-PASS SCRAPER
# ════════════════════════════════════════════════════════════════════

def _fetch_page(url):
    try:
        # aggressive cache-busting to ensure truly fresh content
        headers = _headers()
        headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        headers['Pragma'] = 'no-cache'
        headers['Expires'] = '0'
        r = requests.get(url, headers=headers, timeout=16)
        if r.status_code == 200:
            return BeautifulSoup(r.content, 'html.parser')
    except:
        pass
    return None

def _collect_headlines(soup, base_url):
    seen, out = set(), []
    for a in soup.find_all('a', href=True):
        href  = a['href'].strip()
        if not href or href.startswith('#') or href.startswith('javascript:'): continue
        title = ' '.join(a.get_text(strip=True).split())
        if not _looks_like_headline(title, href): continue
        full  = _abs_url(base_url, href)
        if full in seen: continue
        seen.add(full)
        out.append((title, full))
    return out

def scrape_one_newspaper(key, info):
    _log(f"  🔍 {info['english']} – fetching …")
    t0 = time.time()

    # PASS 1 – headlines from homepage + sections (parallel fetch)
    pages = [info['url']] + info.get('sections', [])
    soups = {}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = {pool.submit(_fetch_page, u): u for u in pages}
        for f in as_completed(futs):
            s = f.result()
            if s: soups[futs[f]] = s

    raw, seen_urls = [], set()
    for page_url, soup in soups.items():
        for title, url in _collect_headlines(soup, page_url):
            if url not in seen_urls:
                seen_urls.add(url)
                raw.append((title, url))

    _log(f"    {info['english']}: {len(raw)} headlines (pass-1)")
    if not raw:
        _log(f"    ⚠️  {info['english']}: zero headlines")
        return []

    # PASS 2 – visit top 50 for content + timestamp (parallel)
    # The rest become headline-only entries
    articles = []
    to_visit = raw[:50]   # visit top 50 for full content
    
    with ThreadPoolExecutor(max_workers=4) as pool:
        fut_map = {pool.submit(_fetch_page, url): (title, url)
                   for title, url in to_visit}
        for f in as_completed(fut_map):
            title, url = fut_map[f]
            asoup      = f.result()
            ts, content, score = None, None, 0
            if asoup:
                ts      = extract_timestamp(asoup, url)
                content = extract_content(asoup)
                # cap content at ~200 words for display
                if content:
                    words = content.split()
                    if len(words) > 200:
                        content = ' '.join(words[:200]) + '…'
                # trending score
                for w in ENGAGEMENT_WORDS:
                    if w in title: score += 25
                if asoup.find(class_=re.compile(r'trending|popular|featured|breaking|top-story', re.I)):
                    score += 120
                if asoup.find(string=re.compile(r'breaking|முக்கியம்|விரைவு', re.I)):
                    score += 100

            articles.append({
                'source':         info['tamil'],
                'sourceEn':       info['english'],
                'sourceKey':      key,
                'title':          title,
                'content':        content or '',
                'url':            url,
                'timestamp':      ts.isoformat() if ts else None,
                'timestamp_raw':  ts,
                'trending_score': score,
                'published_time': ts.strftime('%I:%M %p, %b %d') if ts else None,
            })

    # add remaining headlines (51+) as headline-only entries
    visited = {a['url'] for a in articles}
    for title, url in raw[50:]:   # everything after the first 50
        if url in visited: continue
        articles.append({
            'source': info['tamil'], 'sourceEn': info['english'],
            'sourceKey': key, 'title': title, 'content': '',
            'url': url, 'timestamp': None, 'timestamp_raw': None,
            'trending_score': 0, 'published_time': None,
        })

    _log(f"    ✅ {info['english']}: {len(articles)} articles ({len([a for a in articles if a['content']])} with content) in {time.time()-t0:.1f}s")
    return articles

# ════════════════════════════════════════════════════════════════════
# FULL SCRAPE  (reads saved selection every time)
# ════════════════════════════════════════════════════════════════════

def full_scrape():
    # ── read current selection from disk ─────────────────────────
    selected = _read_selection()
    # keep NEWSPAPERS insertion order but only selected keys
    to_scrape = {k: NEWSPAPERS[k] for k in NEWSPAPERS if k in selected}

    _log("\n" + "="*70)
    _log(f"🔴 SCRAPE STARTED  –  {datetime.now().strftime('%H:%M:%S')}")
    _log(f"   Papers ({len(to_scrape)}): {', '.join(to_scrape[k]['english'] for k in to_scrape)}")
    _log("="*70)
    t0 = time.time()

    raw = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futs = {pool.submit(scrape_one_newspaper, k, v): k for k, v in to_scrape.items()}
        for f in as_completed(futs):
            try:  raw.extend(f.result())
            except Exception as e: _log(f"    ❌ thread error: {e}")

    # ── dedup by URL ──────────────────────────────────────────────
    seen_urls = set()
    unique    = []
    for a in raw:
        if a['url'] not in seen_urls:
            seen_urls.add(a['url'])
            unique.append(a)

    # ── dedup by similar title (first 55 normalised chars) ────────
    seen_titles = set()
    deduped     = []
    for a in unique:
        norm = ' '.join(a['title'].lower().split())[:55]
        if norm in seen_titles:
            continue
        seen_titles.add(norm)
        deduped.append(a)

    # ── sort: GROUP BY NEWSPAPER  (priority order) ────────────────
    # Within each newspaper, trending articles first (by score desc),
    # then rest by timestamp desc.
    # This gives: [all Dinamalar, all Daily Thanthi, all Hindu, ...]
    # with trending articles at the top of each group.
    
    def _ts(a): return a['timestamp_raw'].timestamp() if a['timestamp_raw'] else 0
    
    # build priority-ordered list of selected keys
    selected_keys = list(to_scrape.keys())   # already in NEWSPAPERS insertion order
    
    # group by sourceKey, preserving newspaper priority
    by_paper = {}
    for key in selected_keys:
        by_paper[key] = []
    for a in deduped:
        if a['sourceKey'] in by_paper:
            by_paper[a['sourceKey']].append(a)
    
    # within each newspaper: trending first, then chronological
    for key in selected_keys:
        articles = by_paper[key]
        trending_ones = [a for a in articles if a['trending_score'] > 0]
        regular_ones  = [a for a in articles if a['trending_score'] <= 0]
        trending_ones.sort(key=lambda a: (-a['trending_score'], -_ts(a)))
        regular_ones.sort(key=lambda a: -_ts(a))
        by_paper[key] = trending_ones + regular_ones
    
    # flatten: all papers in priority order
    ordered = []
    for key in selected_keys:
        ordered.extend(by_paper[key])

    # ── number & flag ─────────────────────────────────────────────
    for i, a in enumerate(ordered, 1):
        a['number']      = i
        a['is_trending'] = a['trending_score'] > 0
        del a['timestamp_raw']          # not JSON-serialisable

    trending_total = sum(1 for a in ordered if a['is_trending'])
    elapsed = time.time() - t0
    _log(f"\n✅ SCRAPE DONE – {len(ordered)} articles "
         f"({trending_total} trending) grouped by {len(selected_keys)} newspapers "
         f"in {elapsed:.0f}s  –  {datetime.now().strftime('%H:%M:%S')}")
    _log("="*70 + "\n")
    return ordered

# ════════════════════════════════════════════════════════════════════
# BACKGROUND LOOP   (server-owned 15-min cycle)
# ════════════════════════════════════════════════════════════════════

def background_loop():
    _log("🟢 Background scrape loop started")
    _log("📥 Initial scrape …")
    data = full_scrape()                   # reads selection
    _write_json(LIVE_NEWS, data)
    _log("📥 news_live.json ready")

    while True:
        _log("⏳ Sleeping 13 min …")
        time.sleep(13 * 60)

        with STATE_LOCK: STATE['is_scraping'] = True
        _log("🔄 13-min mark – background scrape …")
        try:
            data = full_scrape()           # re-reads selection every cycle
            _write_json(TEMP_NEWS, data)
            _log(f"📝 Wrote {len(data)} articles → news_temp.json")
        except Exception as e:
            _log(f"❌ background scrape error: {e}")
            data = None
        finally:
            with STATE_LOCK:
                STATE['is_scraping'] = False
                STATE['last_scrape'] = datetime.now()

        _log("⏳ Sleeping 2 min …")
        time.sleep(2 * 60)

        if data:
            _write_json(LIVE_NEWS, data)
            _log("🔀 SWAPPED temp → live")

# ─── JSON helpers ───────────────────────────────────────────────────
def _write_json(path, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, default=str)
    os.replace(tmp, path)

def _read_json(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# ════════════════════════════════════════════════════════════════════
# FLASK ROUTES
# ════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    if os.path.exists(MAIN_HTML):
        return send_file(MAIN_HTML)
    return "<h2>tamil-news-dashboard-final.html not found</h2>", 404

# ── newspaper catalogue  &  user selection ─────────────────────────
@app.route('/api/newspapers', methods=['GET'])
def get_newspapers():
    """Full catalogue in priority order, each with its selected flag."""
    selected = _read_selection()
    catalogue = []
    for key, info in NEWSPAPERS.items():          # dict order = priority
        catalogue.append({
            'key':      key,
            'tamil':    info['tamil'],
            'english':  info['english'],
            'selected': key in selected,
        })
    return jsonify({'newspapers': catalogue})

@app.route('/api/newspapers', methods=['POST'])
def save_newspapers():
    """Persist the user's checkbox selection to disk."""
    try:
        body = request.get_json(force=True)
        keys = [k for k in body.get('selected', []) if k in NEWSPAPERS]
        if not keys:
            keys = list(DEFAULT_SELECTED)     # safety: never empty
        _write_selection(keys)
        _log(f"💾 Selection saved: {keys}")
        return jsonify({'status': 'saved', 'selected': keys})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ── news feed ───────────────────────────────────────────────────────
@app.route('/api/news')
def api_news():
    mode = request.args.get('mode', 'live')
    if mode == 'fresh':
        _log("🟠 FRESH scrape (manual)")
        data = full_scrape()
        _write_json(LIVE_NEWS, data)
    else:
        data = _read_json(LIVE_NEWS)

    return jsonify({
        'status':      'success',
        'total_count': len(data),
        'categories':  {'all_news': data},
        'timestamp':   datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'mode':        mode,
    })

# ── status (JS poller) ──────────────────────────────────────────────
@app.route('/api/status')
def api_status():
    live_mtime = 0
    if os.path.exists(LIVE_NEWS):
        live_mtime = os.path.getmtime(LIVE_NEWS)
    with STATE_LOCK:
        return jsonify({
            'is_scraping': STATE['is_scraping'],
            'last_scrape': STATE['last_scrape'].isoformat() if STATE['last_scrape'] else None,
            'live_mtime':  live_mtime,
            'progress':    STATE['scrape_progress'],
        })

# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥  TAMIL NEWS DASHBOARD – FINAL VERSION")
    print("="*70)
    print("✓  Two-pass scraper – catches ALL headline styles")
    print("✓  Server owns the 15-min refresh cycle (works with tab closed)")
    print("✓  User newspaper selection persisted → user_newspapers.json")
    print("✓  Trending first, then headlines by publish-time")
    print("="*70)
    print(f"🌐  Open:  http://localhost:5000")
    print("="*70 + "\n")

    if date_parser is None:
        print("⚠️  pip install python-dateutil  →  better timestamp parsing\n")

    t = threading.Thread(target=background_loop, daemon=True)
    t.start()

    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"\n❌ {e}")
        input("Press Enter to exit …")
