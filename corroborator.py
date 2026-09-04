from __future__ import annotations
import os, re, httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .discovery import sitemap_urls, HEADERS
from .config import HTTP_TIMEOUT

SEARCH_API_URL = os.getenv("SEARCH_API_URL")
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")

def host(u: str) -> str:
    return (urlparse(u).hostname or "").lower().removeprefix("www.")

def domain_from_url(u: str) -> str:
    h = host(u)
    parts = h.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else h

def title_tokens(title: str) -> set[str]:
    stop = {"official","rules","sweepstakes","giveaway","contest","the","and","for","with","a","an","of","to"}
    return {x for x in re.findall(r"[a-z0-9]+", title.lower()) if len(x) >= 4 and x not in stop}

async def corroborate_on_official_site(title: str, rules_url: str) -> bool:
    """
    Looks for a SECOND, distinct page on the same official sponsor domain.
    This is deliberately conservative: the rules page cannot corroborate itself.
    """
    domain = domain_from_url(rules_url)
    tokens = title_tokens(title)
    if not domain or len(tokens) < 1:
        return False

    async with httpx.AsyncClient(headers=HEADERS, timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        urls = await sitemap_urls(client, domain)
        # Broaden with site home page links if sitemap is sparse.
        try:
            r = await client.get(f"https://www.{domain}")
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = str(httpx.URL(str(r.url)).join(a["href"]))
                    if domain_from_url(href) == domain and href not in urls:
                        urls.append(href)
        except Exception:
            pass

        checked = 0
        for u in urls:
            if u.rstrip("/") == rules_url.rstrip("/"):
                continue
            if checked >= 40:
                break
            # Prefer candidate URLs that share a meaningful title token.
            ul = u.lower()
            if tokens and not any(t in ul for t in tokens):
                continue
            checked += 1
            try:
                r = await client.get(u)
                if r.status_code != 200:
                    continue
                text = " ".join(BeautifulSoup(r.text, "html.parser").stripped_strings).lower()
                hits = sum(1 for t in tokens if t in text)
                if hits >= max(1, min(2, len(tokens))):
                    if any(k in text for k in ("sweepstakes", "giveaway", "contest", "promotion")):
                        return True
            except Exception:
                continue
    return False

async def corroborate_via_search(title: str, rules_url: str) -> bool:
    if not SEARCH_API_URL or not SEARCH_API_KEY:
        return False
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            r = await client.get(
                SEARCH_API_URL,
                params={"q": f'"{title}" official sweepstakes'},
                headers={"Authorization": f"Bearer {SEARCH_API_KEY}"}
            )
            r.raise_for_status()
            data = r.json()
            source = host(rules_url)
            for item in data.get("results", []):
                u = item.get("url", "")
                if u and host(u) != source:
                    return True
    except Exception:
        return False
    return False

async def corroborate(title: str, rules_url: str) -> bool:
    # First use another official page. External search is only a fallback/extra signal.
    if await corroborate_on_official_site(title, rules_url):
        return True
    return await corroborate_via_search(title, rules_url)
