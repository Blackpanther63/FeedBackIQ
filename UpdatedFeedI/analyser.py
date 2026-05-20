import re
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords

nltk.download('vader_lexicon', quiet=True)
nltk.download('stopwords', quiet=True)

sia = SentimentIntensityAnalyzer()

# 'good', 'great', 'nice', 'bad' intentionally NOT in _STOP — they appear in
# KEYWORDS and must be allowed through to sentiment_keywords extraction.
_STOP = set(stopwords.words('english')) | {
    'product', 'item', 'one', 'get', 'got', 'use', 'used', 'using',
    'would', 'could', 'also', 'like', 'really', 'very', 'much',
    'even', 'still', 'well', 'just', 'buy', 'bought', 'ordered',
    'order', 'delivery', 'delivered', 'amazon', 'flipkart', 'seller',
    'price', 'money', 'review', 'reviews', 'recommend', 'star', 'stars',
    'okay', 'bit', 'lot',
}

KEYWORDS = [
    # positive
    "good", "great", "nice", "excellent", "perfect", "amazing",
    "awesome", "quality", "fast", "original", "value",
    # negative
    "bad", "poor", "worst", "damaged", "broken", "fake",
    "slow", "waste", "defective", "useless", "terrible",
    "horrible", "disappointing", "cheap", "pathetic", "refund",
]


def _clean_review(text):
    """Strip rating artifacts like '5.0 out of 5 stars' that slip through from scrapers."""
    text = re.sub(r'[\d.]+\s*out of\s*\d+\s*stars', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip().strip('"').strip()
    return text


def _extract_words(text):
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return [w for w in words if w not in _STOP]


def _top_keywords(word_lists, n=8):
    counter = Counter()
    for words in word_lists:
        counter.update(words)
    return [word for word, _ in counter.most_common(n)]


def analyze_reviews(reviews):
    # ── Deduplicate and strip empty reviews ──────────────────────
    seen = set()
    clean = []
    for r in reviews:
        r = _clean_review(r)
        if r and r not in seen:
            seen.add(r)
            clean.append(r)
    reviews = clean

    print(f"[Analyser] Reviews after dedup/clean: {len(reviews)}")

    result = {
        "positive": 0,
        "negative": 0,
        "neutral": 0,
        "keywords": {k: 0 for k in KEYWORDS},
        "sentiment_keywords": {"positive": [], "negative": [], "neutral": []},
    }

    pos_words, neg_words, neu_words = [], [], []

    for i, review in enumerate(reviews):
        review_lower = review.lower()
        score = sia.polarity_scores(review)
        words = _extract_words(review)

        # compound >= 0.05 → Positive, <= -0.05 → Negative, else Neutral
        if score['compound'] >= 0.05:
            label = "positive"
            result["positive"] += 1
            pos_words.append(words)
        elif score['compound'] <= -0.05:
            label = "negative"
            result["negative"] += 1
            neg_words.append(words)
        else:
            label = "neutral"
            result["neutral"] += 1
            neu_words.append(words)

        print(f"[Analyser] [{i+1:02d}] {label:8s} compound={score['compound']:+.3f} | {review[:90]}")

        for key in KEYWORDS:
            if key in review_lower:
                result["keywords"][key] += 1

    total = result["positive"] + result["negative"] + result["neutral"]
    if total:
        print(
            f"[Analyser] Summary → "
            f"Pos={result['positive']} ({result['positive']/total*100:.1f}%) | "
            f"Neg={result['negative']} ({result['negative']/total*100:.1f}%) | "
            f"Neu={result['neutral']} ({result['neutral']/total*100:.1f}%)"
        )

    result["keywords"] = {k: v for k, v in result["keywords"].items() if v > 0}
    result["sentiment_keywords"] = {
        "positive": _top_keywords(pos_words),
        "negative": _top_keywords(neg_words),
        "neutral":  _top_keywords(neu_words),
    }
    return result
