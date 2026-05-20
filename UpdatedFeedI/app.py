from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from analyser import analyze_reviews
from scraper import scrape_product, get_product_link, _make_driver
from sales import estimate_sales_impact, generate_sales_chart
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import threading
import urllib.parse
import secrets
from selenium.webdriver.common.by import By

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ── Server-side filesystem session (no 4KB cookie limit) ───────
app.config["SESSION_TYPE"]           = "filesystem"
app.config["SESSION_FILE_DIR"]       = os.path.join(os.path.dirname(__file__), "flask_sessions")
app.config["SESSION_PERMANENT"]      = False
app.config["SESSION_USE_SIGNER"]     = True
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)
Session(app)

if not os.path.exists("static"):
    os.makedirs("static")


# ── Featured product thumbnail prefetch ────────────────────────

FEATURED_PRODUCTS = [
    "boAt Rockerz 255 Pro Wireless Earphones",
    "JBL C100SI In-Ear Headphones",
    "Noise ColorFit Pro 4 Smartwatch",
    "Redmi Note 13 5G Smartphone",
    "Oneplus Nord Buds 2 TWS Earbuds",
    "Philips Hair Dryer HP8100",
]

_thumb_cache: dict = {}   # product name → image URL


def _prefetch_images():
    driver = _make_driver()
    try:
        for name in FEATURED_PRODUCTS:
            if name in _thumb_cache:
                continue
            try:
                query = urllib.parse.quote(name)
                driver.get(f"https://www.amazon.in/s?k={query}")
                import time; time.sleep(2)
                for img in driver.find_elements(By.CSS_SELECTOR, "img.s-image"):
                    src = img.get_attribute("src") or ""
                    if src.startswith("http"):
                        _thumb_cache[name] = src
                        break
            except Exception:
                pass
    finally:
        driver.quit()


threading.Thread(target=_prefetch_images, daemon=True).start()


@app.route("/api/product-image")
def product_image_api():
    name = request.args.get("q", "").strip()
    return jsonify({"url": _thumb_cache.get(name)})


# ── Graphs ─────────────────────────────────────────────────────

def generate_graphs(result):
    all_labels = ['Positive', 'Negative', 'Neutral']
    all_values = [result['positive'], result['negative'], result['neutral']]
    all_colors = ['#4ade80', '#f87171', '#94a3b8']

    total_val = sum(all_values) if sum(all_values) > 0 else 1
    # Use a tiny floor so zero-value categories still render as a visible sliver
    plot_values = [max(v, 0.01) for v in all_values] if sum(all_values) > 0 else [1, 0.01, 0.01]
    labels_with_pct = [f"{l} ({v/total_val*100:.1f}%)" for l, v in zip(all_labels, all_values)]

    _, ax = plt.subplots(figsize=(6.5, 3.5))
    wedges, _ = ax.pie(
        plot_values,
        colors=all_colors,
        startangle=90,
        wedgeprops=dict(linewidth=1.5, edgecolor='white'),
    )
    
    legend = ax.legend(
        wedges,
        labels_with_pct,
        title="Distribution",
        loc="center left",
        bbox_to_anchor=(0.95, 0.5),
        frameon=False,
        fontsize=10
    )
    legend.get_title().set_fontweight('bold')
    legend.get_title().set_fontsize(11)

    ax.set_title("Sentiment Analysis", fontsize=13, fontweight='bold', pad=14)
    plt.savefig("static/sentiment.png", bbox_inches="tight", dpi=120)
    plt.close()

    keywords = {k: v for k, v in result['keywords'].items() if v > 0}
    _, ax = plt.subplots(figsize=(6.5, 3.5))
    if keywords:
        keys   = list(keywords.keys())
        counts = list(keywords.values())
        bars = ax.bar(keys, counts, color='#2563eb', width=0.6, edgecolor='white')
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                    str(count), ha='center', va='bottom', fontsize=9,
                    fontweight='bold', color='#1e293b')
        ax.set_ylabel("Mentions", fontsize=10)
        ax.set_title("Top Keywords in Reviews", fontsize=13, fontweight='bold')
        ax.set_ylim(0, max(counts) * 1.25)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=35, ha='right', fontsize=9)
    else:
        ax.text(0.5, 0.5, 'No keywords found', ha='center', va='center',
                transform=ax.transAxes, color='#94a3b8', fontsize=13)
        ax.axis('off')
    plt.tight_layout()
    plt.savefig("static/keywords.png", bbox_inches="tight", dpi=120)
    plt.close()


def calculate_rating(result):
    total = result['positive'] + result['negative'] + result['neutral']
    if total == 0:
        return 0
    score = (result['positive'] * 5 + result['neutral'] * 3 + result['negative'] * 1) / total
    return round(score, 1)


# ── Routes ─────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    data = session.pop("result_data", None)
    if data:
        return render_template("index.html", **data)
    return render_template("index.html", result=None)


@app.route("/analyze", methods=["POST"])
def analyze():
    product_input = request.form.get("product", "").strip()

    if not product_input:
        session["result_data"] = {"result": None, "error": "Please enter a product URL."}
        return redirect(url_for("home"))

    PLATFORM_DOMAINS = ("amazon.", "flipkart.", "myntra.", "snapdeal.")

    if product_input.startswith("http://") or product_input.startswith("https://"):
        product_url = product_input
    elif any(d in product_input for d in PLATFORM_DOMAINS):
        # URL pasted without protocol prefix — add https://
        product_url = "https://" + product_input.lstrip("/")
    else:
        query       = urllib.parse.quote(product_input)
        product_url = get_product_link(f"https://www.amazon.in/s?k={query}")

    if not product_url:
        session["result_data"] = {
            "result": None,
            "error":  "Could not find a product. Try pasting the product link directly."
        }
        return redirect(url_for("home"))

    data = scrape_product(product_url)

    if data.get("error"):
        session["result_data"] = {"result": None, "error": data["error"]}
        return redirect(url_for("home"))

    if not data["reviews"]:
        platform = data.get("platform", "unknown")
        if platform == "amazon":
            msg = ("Amazon blocked the request (bot protection). "
                   "Wait 30–60 seconds and try again, or paste a Flipkart link for the same product.")
        else:
            msg = "No reviews found. The site may have blocked the request, or this product has no English reviews yet."
        session["result_data"] = {"result": None, "error": msg}
        return redirect(url_for("home"))

    reviews       = data["reviews"]
    display_name  = data["title"] or product_input
    product_image = data["image"]

    texts  = [r["text"] for r in reviews]
    result = analyze_reviews(texts)
    generate_graphs(result)
    rating = calculate_rating(result)
    impact = estimate_sales_impact(result, rating)
    if impact:
        generate_sales_chart(impact)

    session["result_data"] = {
        "result":        result,
        "reviews":       reviews[:10],
        "rating":        rating,
        "product_name":  display_name,
        "product_image": product_image,
        "total_reviews": len(reviews),
        "impact":        impact,
        "platform":      data.get("platform", "unknown"),
    }
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=5005)
