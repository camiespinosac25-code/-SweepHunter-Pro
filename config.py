import os, json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("SWEEPHUNTER_DB", str(BASE_DIR / "data" / "sweephunter.sqlite3"))

# Curated high-trust sponsor domains. Add/remove without changing scanner code.
TRUSTED_DOMAINS = [
    d.strip().lower() for d in os.getenv(
        "TRUSTED_DOMAINS",
        "coca-cola.com,pepsico.com,starbucks.com,hilton.com,marriott.com,"
        "southwest.com,delta.com,united.com,disney.com,nike.com,target.com,"
        "walmart.com,bestbuy.com,lowes.com,homedepot.com"
    ).split(",") if d.strip()
]

KEYWORDS = ("sweepstakes", "sweepstake", "giveaway", "contest", "official-rules", "official_rules")

SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "60"))
MAX_URLS_PER_DOMAIN = int(os.getenv("MAX_URLS_PER_DOMAIN", "150"))
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "15"))

# APNs - optional until deployed.
APNS_TEAM_ID = os.getenv("APNS_TEAM_ID")
APNS_KEY_ID = os.getenv("APNS_KEY_ID")
APNS_BUNDLE_ID = os.getenv("APNS_BUNDLE_ID")
APNS_PRIVATE_KEY_PATH = os.getenv("APNS_PRIVATE_KEY_PATH")
APNS_USE_SANDBOX = os.getenv("APNS_USE_SANDBOX", "1") == "1"
