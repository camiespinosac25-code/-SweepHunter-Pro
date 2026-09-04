from __future__ import annotations
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
from .models import CandidateGiveaway
from .config import TRUSTED_DOMAINS

NO_PURCHASE = [
    "no purchase or payment of any kind is necessary",
    "no purchase necessary",
    "no purchase is necessary"
]
ACCOUNT_PATTERNS = [
    r"\bcreate (?:an?|your) account\b",
    r"\bregister for (?:an?|your) account\b",
    r"\blog in or create\b",
    r"\bsign up for (?:an?|your) account\b",
]
APP_PATTERNS = [
    r"\bapp download is required\b",
    r"\bdownload (?:the|our|an) app\b",
    r"\binstall (?:the|our|an) app\b",
]
NEWSLETTER_PATTERNS = [r"\bsubscribe\b.*\bnewsletter\b", r"\bnewsletter subscription\b"]
THIRD_PARTY_PATTERNS = [
    r"\bcomplete (?:an?|the) offer\b",
    r"\bcomplete offers\b",
    r"\bthird[- ]party registration\b",
]
FINANCIAL_PATTERNS = [
    r"\bcredit card\b", r"\bdebit card\b", r"\bbank account\b",
    r"\brouting number\b", r"\bpayment information\b"
]
SSN_PATTERNS = [r"\bsocial security number\b", r"\bssn\b"]
ID_PATTERNS = [r"\bdriver'?s license\b", r"\bpassport\b", r"\bgovernment[- ]issued id\b"]

def base_domain(host: str) -> str:
    host = host.lower().split(":")[0]
    return host[4:] if host.startswith("www.") else host

def trusted_host(url: str) -> bool:
    host = base_domain(urlparse(url).hostname or "")
    return any(host == d or host.endswith("." + d) for d in TRUSTED_DOMAINS)

def any_re(patterns, text):
    return any(re.search(p, text, re.I | re.S) for p in patterns)

def extract_candidate(url: str, html: str) -> CandidateGiveaway | None:
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.stripped_strings)
    lower = text.lower()

    if "official rules" not in lower:
        return None
    if "sweepstakes" not in lower and "contest" not in lower and "giveaway" not in lower:
        return None

    title = (soup.find("h1").get_text(" ", strip=True) if soup.find("h1")
             else (soup.title.get_text(" ", strip=True) if soup.title else "Official Sweepstakes"))

    # Strong requirement: actual no-purchase language.
    no_purchase = any(p in lower for p in NO_PURCHASE)

    # Sponsor: best-effort extraction.
    sponsor = base_domain(urlparse(url).hostname or "")
    sponsor_match = re.search(r'(?:Sponsor(?:ed)?(?: by)?[:\s]+)([A-Z][^.;]{2,100})', text)
    if sponsor_match:
        sponsor = sponsor_match.group(1).strip()

    # Eligibility regions
    regions = []
    if re.search(r'50 (?:United )?States and (?:the )?(?:District of Columbia|D\.?C\.?)', text, re.I):
        regions = ["US-50", "DC"]

    age = None
    m = re.search(r'(\d{1,2}) years? of age or older', text, re.I)
    if m:
        age = int(m.group(1))

    # Dates: conservative; only populate when obvious.
    end_date = None
    m = re.search(r'ends? (?:at .*? on |on )([A-Z][a-z]+ \d{1,2}, 20\d{2})', text)
    if m:
        try: end_date = dtparser.parse(m.group(1))
        except Exception: pass

    # Entry link: choose explicit "enter" link if present, else rules URL.
    entry_url = url
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        if any(k in label for k in ["enter now", "enter sweepstakes", "enter here", "enter"]):
            entry_url = urljoin(url, a["href"])
            break

    # These are hard rejects in our user's strict mode.
    requires_account = any_re(ACCOUNT_PATTERNS, text)
    requires_app = any_re(APP_PATTERNS, text)
    requires_newsletter = any_re(NEWSLETTER_PATTERNS, text)
    requires_third_party = any_re(THIRD_PARTY_PATTERNS, text)
    financial = any_re(FINANCIAL_PATTERNS, text)
    ssn = any_re(SSN_PATTERNS, text)
    gov_id = any_re(ID_PATTERNS, text)

    # Purchase requirement is false only if explicit NPN language exists.
    requires_purchase = not no_purchase

    # Cross-source starts false. corroborator.py must prove it.
    return CandidateGiveaway(
        title=title,
        sponsor=sponsor,
        entry_url=entry_url,
        official_rules_url=url,
        end_date=end_date,
        eligible_regions=regions,
        minimum_age=age,
        entry_method="web",
        requires_purchase=requires_purchase,
        requires_account_creation=requires_account,
        requires_app_install=requires_app,
        requires_newsletter=requires_newsletter,
        requires_third_party_registration=requires_third_party,
        requires_financial_info=financial,
        requires_ssn=ssn,
        requires_government_id_at_entry=gov_id,
        sponsor_domain_verified=trusted_host(url),
        rules_verified=True,
        cross_source_verified=False,
        required_fields=[],
    )
