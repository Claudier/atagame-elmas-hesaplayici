from flask import Flask, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
import time
from threading import Lock

app = Flask(__name__)

SOURCE_URL = "https://www.atagame.net/mobile-legends-bang-bang-tr-c-132/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DiamondPriceChecker/1.0)",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}
CACHE_SECONDS = 600
_cache = {"at": 0, "products": None, "error": None}
_lock = Lock()

# Son bilinen fiyatlar: kaynak siteye erişilemediğinde yedek olarak gösterilir.
FALLBACK = [
    {"diamonds": 16, "price": 11.49},
    {"diamonds": 32, "price": 22.99},
    {"diamonds": 44, "price": 30.99},
    {"diamonds": 88, "price": 62.99},
    {"diamonds": 133, "price": 94.99},
    {"diamonds": 221, "price": 159.99},
    {"diamonds": 309, "price": 219.99},
    {"diamonds": 354, "price": 249.99},
    {"diamonds": 494, "price": 349.99},
    {"diamonds": 627, "price": 449.99},
    {"diamonds": 715, "price": 509.99},
    {"diamonds": 1041, "price": 699.99},
    {"diamonds": 1535, "price": 1049.99},
    {"diamonds": 2645, "price": 1759.99},
    {"diamonds": 2866, "price": 1899.99},
    {"diamonds": 3139, "price": 2099.99},
    {"diamonds": 3686, "price": 2449.99},
    {"diamonds": 5290, "price": 3499.99},
    {"diamonds": 6146, "price": 3999.99},
    {"diamonds": 6640, "price": 4369.99},
    {"diamonds": 7187, "price": 4699.99},
    {"diamonds": 8791, "price": 5749.99},
    {"diamonds": 12292, "price": 7999.99},
    {"diamonds": 18438, "price": 11999.99},
    {"diamonds": 24584, "price": 15999.99},
]

def tr_price(value):
    """'1.049,99' veya '1049,99' biçimini float'a çevirir."""
    value = value.strip().replace("TL", "").replace("₺", "").replace(" ", "")
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    return float(value)

def scrape_products():
    response = requests.get(SOURCE_URL, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    found = {}
    # Atagame sayfasındaki ürün başlıklarını ve aynı ürün kartındaki fiyatı bul.
    for node in soup.find_all(string=re.compile(r"^\s*[\d.]+\s*Elmas\s*$", re.I)):
        title = str(node).strip()
        match = re.search(r"([\d.]+)\s*Elmas", title, re.I)
        if not match:
            continue
        diamonds = int(match.group(1).replace(".", ""))

        parent = node.parent
        best_text = ""
        for _ in range(7):
            if parent is None:
                break
            candidate = " ".join(parent.stripped_strings)
            if re.search(r"\d[\d.]*,\d{2}\s*(?:TL|₺)", candidate):
                best_text = candidate
                break
            parent = parent.parent

        if not best_text:
            continue

        prices = re.findall(r"(\d[\d.]*,\d{2})\s*(?:TL|₺)", best_text)
        if not prices:
            continue
        # Kartta indirimli fiyat genellikle son fiyat olarak yer alır.
        try:
            price = tr_price(prices[-1])
        except ValueError:
            continue
        if diamonds > 0 and price > 0:
            found[diamonds] = {"diamonds": diamonds, "price": price}

    products = sorted(found.values(), key=lambda item: item["diamonds"])
    if len(products) < 5:
        raise RuntimeError("Sayfadaki ürün/fiyat yapısı beklenen biçimde okunamadı.")
    return products

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/prices")
def prices():
    now = time.time()
    with _lock:
        if _cache["products"] and now - _cache["at"] < CACHE_SECONDS:
            return jsonify({
                "products": _cache["products"],
                "updated_at": _cache["at"],
                "source": SOURCE_URL,
                "cached": True,
                "fallback": False,
            })

        try:
            products = scrape_products()
            _cache.update({"at": now, "products": products, "error": None})
            return jsonify({
                "products": products,
                "updated_at": now,
                "source": SOURCE_URL,
                "cached": False,
                "fallback": False,
            })
        except Exception as exc:
            # Önceki başarılı veri varsa onu, yoksa son bilinen listeyi sun.
            products = _cache["products"] or FALLBACK
            return jsonify({
                "products": products,
                "updated_at": _cache["at"] or None,
                "source": SOURCE_URL,
                "cached": bool(_cache["products"]),
                "fallback": not bool(_cache["products"]),
                "warning": "Atagame'ye şu an erişilemedi; son bilinen fiyatlar gösteriliyor.",
            })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
