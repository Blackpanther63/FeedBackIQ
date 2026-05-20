import re
import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chromedriver.exe")



# ─────────────────────────── driver ────────────────────────────

def _make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en-US,en;q=0.9")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36"
    )
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = { runtime: {} };
        """
    })
    return driver


def _human_sleep(lo=2.0, hi=4.0):
    time.sleep(random.uniform(lo, hi))


def _is_blocked(driver):
    """Return True if Amazon is showing a CAPTCHA or robot-check page."""
    src = driver.page_source.lower()
    return any(k in src for k in [
        "enter the characters you see below",
        "sorry, we just need to make sure",
        "robot check",
        "captcha",
        "api-services-support@amazon",
    ])


# ─────────────────────────── helpers ───────────────────────────

def _detect_platform(url):
    if "amazon."    in url: return "amazon"
    if "flipkart."  in url: return "flipkart"
    if "myntra."    in url: return "myntra"
    if "snapdeal."  in url: return "snapdeal"
    return "unknown"


def _is_english(text):
    if not text:
        return False
    return sum(1 for c in text if ord(c) < 128) / len(text) >= 0.80


# ══════════════════════════════════════════════════════════════
#  AMAZON
# ══════════════════════════════════════════════════════════════

def _scrape_amazon(driver, url):
    domain_m = re.search(r"(https?://(?:www\.)?amazon\.[a-z.]+)/", url)
    domain = domain_m.group(1) if domain_m else "https://www.amazon.in"

    driver.get(domain)
    _human_sleep(2, 3.5)
    driver.get(url)
    _human_sleep(3, 5)

    if _is_blocked(driver):
        print("[Scraper][Amazon] Blocked on product page.")
        return None, None, []

    # Title
    title = None
    for sel in ["#productTitle", "#title"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            title = el.text.strip()
            if title:
                break
        except Exception:
            pass

    # Image
    image_url = None
    for sel in ["#landingImage", "#imgBlkFront", "#main-image"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            raw = (el.get_attribute("data-a-dynamic-image")
                   or el.get_attribute("data-old-hires")
                   or el.get_attribute("src"))
            if raw and raw.startswith("{"):
                image_url = list(json.loads(raw).keys())[0]
            elif raw:
                image_url = raw
            if image_url:
                break
        except Exception:
            pass

    # ASIN — handles both /dp/ and /gp/product/ URL formats
    asin_m = re.search(r'(?:/dp/|/gp/product/)([A-Z0-9]{10})', url)
    asin = asin_m.group(1) if asin_m else None
    print(f"[Scraper][Amazon] ASIN={asin}  domain={domain}")

    def _collect_page_reviews(seen):
        """Collect all review cards visible on the current page."""
        found = []
        for scroll_y in ["document.body.scrollHeight * 0.5",
                          "document.body.scrollHeight"]:
            driver.execute_script(f"window.scrollTo(0, {scroll_y})")
            _human_sleep(0.8, 1.5)

        for sel in ["li[data-hook='review']", "div[data-hook='review']"]:
            for card in driver.find_elements(By.CSS_SELECTOR, sel):
                # ── Reviewer name (actual username, e.g. "Rahul K.") ──
                try:
                    name = card.find_element(
                        By.CSS_SELECTOR, "span.a-profile-name"
                    ).text.strip() or "Anonymous"
                except Exception:
                    name = "Anonymous"

                # ── Review title / headline (e.g. "Brilliant!") ──
                # This is separate from the reviewer name — scrape it
                # explicitly so it can be displayed as a card heading.
                rtitle = ""
                try:
                    for tspan in card.find_elements(
                        By.CSS_SELECTOR, "[data-hook='review-title'] span"
                    ):
                        txt = tspan.text.strip()
                        if txt and "out of" not in txt.lower():
                            rtitle = txt
                            break
                except Exception:
                    pass

                # ── Review body ──
                try:
                    body = card.find_element(
                        By.CSS_SELECTOR, "span[data-hook='review-body']"
                    ).text.strip()
                    body = re.sub(
                        r'[\d.]+\s*out of\s*\d+\s*stars\s*',
                        '', body, flags=re.IGNORECASE
                    ).strip().strip('"').strip()
                except Exception:
                    continue

                if body and len(body) > 15 and body not in seen and _is_english(body):
                    seen.add(body)
                    found.append({"name": name, "title": rtitle, "text": body})
        return found

    # ── Step 1: product page "top reviews" (usually positive) ──
    seen_texts = set()
    reviews = _collect_page_reviews(seen_texts)
    print(f"[Scraper][Amazon] Product page reviews: {len(reviews)}")

    # ── Step 2: dedicated review pages for a balanced picture ──
    # Paginate every filter until the page returns 0 new reviews (natural end).
    # High page caps (50) prevent infinite loops; early-exit handles products
    # with fewer pages.
    if asin:
        blocked = False
        # (filter_param, max_pages)  — paginate until empty or cap is hit
        fetch_plan = [
            ("sortBy=recent",            50),  # all recent mixed reviews
            ("filterByStar=critical",    20),  # all 1-2 star reviews
            ("filterByStar=one_star",    20),  # all 1-star reviews
            ("filterByStar=two_star",    20),  # all 2-star reviews
            ("filterByStar=three_star",  20),  # all 3-star (neutral) reviews
            ("filterByStar=four_star",   20),  # all 4-star reviews
        ]
        for filter_param, max_pages in fetch_plan:
            if blocked:
                break
            for page_num in range(1, max_pages + 1):
                try:
                    rev_url = (
                        f"{domain}/product-reviews/{asin}"
                        f"?{filter_param}&pageNumber={page_num}"
                    )
                    driver.get(rev_url)
                    _human_sleep(2.5, 4.5)
                    if _is_blocked(driver):
                        print("[Scraper][Amazon] Blocked on review page — stopping.")
                        blocked = True
                        break
                    page_revs = _collect_page_reviews(seen_texts)
                    print(
                        f"[Scraper][Amazon] filter={filter_param} "
                        f"page={page_num} → {len(page_revs)} new reviews "
                        f"(total so far: {len(reviews) + len(page_revs)})"
                    )
                    if not page_revs and page_num > 1:
                        break  # no more pages for this filter
                    reviews.extend(page_revs)
                except Exception as exc:
                    print(f"[Scraper][Amazon] Error fetching {filter_param} p{page_num}: {exc}")
                    break

    print(f"[Scraper][Amazon] Total reviews collected: {len(reviews)}")
    for i, r in enumerate(reviews[:5]):
        print(f"[Scraper][Amazon] Sample {i+1}: {r['text'][:100]}")

    return title, image_url, reviews


# ══════════════════════════════════════════════════════════════
#  FLIPKART
# ══════════════════════════════════════════════════════════════

def _flipkart_reviews_url(url):
    clean = url.split("?")[0].rstrip("/")
    m = re.search(r"/p/(itm[A-Za-z0-9]+)", clean)
    if m:
        slug_m = re.search(r"flipkart\.com/([^/]+)/", clean)
        slug = slug_m.group(1) if slug_m else "product"
        return f"https://www.flipkart.com/{slug}/product-reviews/{m.group(1)}"
    return url


def _scrape_flipkart(driver, url):
    driver.get(url)
    time.sleep(3)

    title = None
    for sel in ["h1", "span.B_NuCI", "span.VU-ZEz"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            t = el.text.strip()
            if t and len(t) > 5:
                title = t
                break
        except Exception:
            pass

    image_url = None
    try:
        for img in driver.find_elements(By.TAG_NAME, "img"):
            src = img.get_attribute("src") or ""
            if "rukminim" in src and "128" not in src:
                image_url = src
                break
    except Exception:
        pass

    reviews_url = _flipkart_reviews_url(url)

    # JavaScript to extract reviews from the current page DOM.
    # Falls through multiple known Flipkart CSS selectors because
    # they use hashed CSS-in-JS class names that change with each deploy.
    _FK_JS = """
        var selectors = [
            'span.css-1jxf684',
            'div.ZmyHeo span',
            'div._6K-7Co span',
            'div[class*="review"] p'
        ];
        var spans = [];
        for (var sel of selectors) {
            var found = document.querySelectorAll(sel);
            if (found.length > 0) { spans = found; break; }
        }
        var results = [];
        for (var span of spans) {
            var text = (span.innerText || "").trim();
            if (!text || text.length < 15) continue;
            var container = null, el = span;
            for (var i = 0; i < 12; i++) {
                el = el.parentElement;
                if (!el) break;
                for (var a of el.attributes) {
                    if (a.name.startsWith("data-observerid")) { container = el; break; }
                }
                if (container) break;
            }
            var reviewTitle = "";
            var name = "Anonymous";
            if (container) {
                var autoDivs = Array.from(container.querySelectorAll("div[dir='auto']"))
                    .map(d => (d.innerText || "").trim()).filter(t => t.length > 0);
                var count = 0;
                for (var t of autoDivs) {
                    if (/^\\d+\\.?\\d*$/.test(t)) continue; // skip numeric ratings
                    if (t.startsWith("Review for")) continue;
                    if (t.startsWith(",")) continue;
                    if (t === "\\u2022") continue;
                    if (t.length > 60) continue;
                    if (t === text) continue; // skip if same as review body
                    count++;
                    if (count === 1) { reviewTitle = t; }       // 1st = review headline
                    else if (count === 2) { name = t; break; }  // 2nd = reviewer name
                }
            }
            results.push({ name: name, title: reviewTitle, text: text });
        }
        return results;
    """

    reviews = []
    seen_texts = set()

    # Paginate until the page returns 0 new reviews (natural end of listings)
    for page_num in range(1, 101):   # cap at 100 pages to avoid infinite loops
        paged_url = f"{reviews_url}?page={page_num}"
        try:
            driver.get(paged_url)
            time.sleep(4)
            raw = driver.execute_script(_FK_JS)
        except Exception as exc:
            print(f"[Scraper][Flipkart] Error on page {page_num}: {exc}")
            break

        page_reviews = []
        for r in (raw or []):
            text  = (r.get("text")  or "").strip()
            name  = (r.get("name")  or "Anonymous").strip() or "Anonymous"
            rtitle = (r.get("title") or "").strip()
            if text and text not in seen_texts and _is_english(text):
                seen_texts.add(text)
                page_reviews.append({"name": name, "title": rtitle, "text": text})

        print(f"[Scraper][Flipkart] page={page_num} → {len(page_reviews)} new reviews "
              f"(total so far: {len(reviews) + len(page_reviews)})")

        if not page_reviews:
            break  # no reviews on this page — end of listings

        reviews.extend(page_reviews)

    print(f"[Scraper][Flipkart] Total reviews collected: {len(reviews)}")
    return title, image_url, reviews


# ══════════════════════════════════════════════════════════════
#  MYNTRA
# ══════════════════════════════════════════════════════════════

def _myntra_product_id(url):
    m = re.search(r'/(\d{6,})/buy', url)
    return m.group(1) if m else None


def _parse_myntra_cards(driver):
    reviews = []
    seen    = set()
    for card in driver.find_elements(By.CSS_SELECTOR, "div.user-review-userReviewWrapper"):
        # Review body
        try:
            text = card.find_element(
                By.CSS_SELECTOR, "div.user-review-reviewTextWrapper"
            ).text.strip()
        except Exception:
            continue

        # Review title (headline written by reviewer)
        rtitle = ""
        try:
            rtitle = card.find_element(
                By.CSS_SELECTOR, "div.user-review-reviewWrapper div.user-review-titleWrapper, "
                                 "h3.user-review-title, div[class*='title']"
            ).text.strip()
        except Exception:
            pass

        # Reviewer name — spans: [rating, name, date]
        name = "Anonymous"
        try:
            spans     = card.find_elements(By.TAG_NAME, "span")
            non_empty = [s.text.strip() for s in spans if s.text.strip()]
            if len(non_empty) >= 2:
                candidate = non_empty[1]
                if not re.search(r'^\d+$|\d{4}|\d+ \w+ \d+', candidate):
                    name = candidate
        except Exception:
            pass

        if text and text not in seen and _is_english(text):
            seen.add(text)
            reviews.append({"name": name, "title": rtitle, "text": text})
    return reviews


def _scrape_myntra(driver, url):
    driver.get(url)
    time.sleep(4)

    brand, pname = "", ""
    try:
        brand = driver.find_element(By.CSS_SELECTOR, "h1.pdp-title").text.strip()
    except Exception:
        pass
    try:
        pname = driver.find_element(By.CSS_SELECTOR, "h1.pdp-name").text.strip()
    except Exception:
        pass
    title = f"{brand} {pname}".strip() or None

    image_url = None
    try:
        for img in driver.find_elements(By.TAG_NAME, "img"):
            src = img.get_attribute("src") or ""
            if ("assets.myntassets.com" in src
                    and "logo" not in src and "banner" not in src
                    and "nav"  not in src and "icon"   not in src):
                src       = re.sub(r'h_\d+,', 'h_500,', src)
                src       = re.sub(r'w_\d+',  'w_500',  src)
                image_url = src
                break
    except Exception:
        pass

    product_id = _myntra_product_id(url)
    if product_id:
        driver.get(f"https://www.myntra.com/reviews/{product_id}")
        time.sleep(4)
    else:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2)")
        time.sleep(2)

    # Scroll and click "Load More" / "Show More" up to 15 times so we
    # accumulate all available reviews before parsing once at the end.
    last_height = 0
    _LOAD_MORE_SELS = [
        "button.user-review-showMoreReviews",
        "div.user-review-showMoreReviews",
        "button[data-testid='show-more-reviews']",
        "a[class*='showMore']",
        "button[class*='showMore']",
        "div[class*='showMore']",
        "button[class*='load-more']",
        "a[class*='load-more']",
    ]
    for scroll_iter in range(15):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        clicked = False
        for btn_sel in _LOAD_MORE_SELS:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, btn_sel)
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", btn
                )
                time.sleep(2)
                clicked = True
                break
            except Exception:
                pass
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"[Scraper][Myntra] scroll iter {scroll_iter+1}: height={new_height} clicked={clicked}")
        if new_height == last_height and not clicked:
            break  # nothing new loaded
        last_height = new_height

    reviews = _parse_myntra_cards(driver)
    print(f"[Scraper][Myntra] Total reviews collected: {len(reviews)}")
    return title, image_url, reviews


# ══════════════════════════════════════════════════════════════
#  SNAPDEAL
# ══════════════════════════════════════════════════════════════

def _scrape_snapdeal(driver, url):
    driver.get(url)
    time.sleep(5)

    title = None
    for sel in ["h1.pdp-e-i-head", "h1", "span[itemprop='name']"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            t = el.text.strip()
            if t and len(t) > 5:
                title = t
                break
        except Exception:
            pass

    image_url = None
    for sel in ["img#main-product-image", "img.cloudzoom", "div.product-thumbnails img"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            src = (el.get_attribute("src")
                   or el.get_attribute("data-src")
                   or "")
            if src:
                image_url = src
                break
        except Exception:
            pass

    # Scroll + click "Load More" / next-page up to 10 times to load all reviews
    _SD_LOAD_MORE = [
        "button.loadMoreReviews", "a.next-reviews",
        "button[class*='loadMore']", "a[class*='nextPage']",
        "div.pagination a[rel='next']", "li.next a",
    ]
    last_height = 0
    for scroll_iter in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        clicked = False
        for btn_sel in _SD_LOAD_MORE:
            try:
                btn = driver.find_element(By.CSS_SELECTOR, btn_sel)
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
                clicked = True
                break
            except Exception:
                pass
        new_height = driver.execute_script("return document.body.scrollHeight")
        print(f"[Scraper][Snapdeal] scroll iter {scroll_iter+1}: height={new_height} clicked={clicked}")
        if new_height == last_height and not clicked:
            break
        last_height = new_height

    reviews = []
    seen_texts = set()
    for sel in ["div.user-review", "div.review-description", "p.review-description"]:
        cards = driver.find_elements(By.CSS_SELECTOR, sel)
        if cards:
            for card in cards:
                text = card.text.strip()
                name = "Anonymous"
                try:
                    name_el = card.find_element(By.CSS_SELECTOR,
                                                ".reviewer-name, .review-author, span.name")
                    name = name_el.text.strip() or "Anonymous"
                except Exception:
                    pass
                if text and len(text) > 15 and text not in seen_texts and _is_english(text):
                    seen_texts.add(text)
                    reviews.append({"name": name, "text": text})
            break

    print(f"[Scraper][Snapdeal] Total reviews collected: {len(reviews)}")
    return title, image_url, reviews


# ══════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════

def get_product_link(search_url):
    """Amazon keyword search → first product URL."""
    driver = _make_driver()
    try:
        driver.get(search_url)
        time.sleep(2)
        for link in driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline"):
            href = link.get_attribute("href")
            if href and "/dp/" in href:
                return href.split("?")[0]
    except Exception:
        pass
    finally:
        driver.quit()
    return None


def scrape_product(url):
    """
    Single browser session. Returns:
      { "title": str|None, "image": str|None, "reviews": [{"name":..,"text":..}] }
    """
    driver = _make_driver()
    try:
        platform = _detect_platform(url)
        print(f"[Scraper] Platform detected: {platform}  URL: {url[:80]}")
        if platform == "amazon":
            title, image, reviews = _scrape_amazon(driver, url)
        elif platform == "flipkart":
            title, image, reviews = _scrape_flipkart(driver, url)
        elif platform == "myntra":
            title, image, reviews = _scrape_myntra(driver, url)
        elif platform == "snapdeal":
            title, image, reviews = _scrape_snapdeal(driver, url)
        else:
            return {"title": None, "image": None, "reviews": [],
                    "error": "Unsupported platform. Paste a link from Amazon, Flipkart, Myntra, or Snapdeal."}
        return {"title": title, "image": image, "reviews": reviews, "platform": platform}
    except Exception as exc:
        print(f"[Scraper] Unhandled exception: {exc}")
        return {"title": None, "image": None, "reviews": [], "platform": "unknown"}
    finally:
        driver.quit()
