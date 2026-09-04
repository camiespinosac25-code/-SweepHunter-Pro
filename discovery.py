from __future__ import annotations
import asyncio, re
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from .config import TRUSTED_DOMAINS, KEYWORDS, MAX_URLS_PER_DOMAIN, HTTP_TIMEOUT

HEADERS = {"User-Agent": "SweepHunter/1.0 (+verification crawler; public official rules only)"}

def looks_relevant(url: str) -> bool:
    u = url.lower()
    return any(k in u for k in KEYWORDS)

async def sitemap_urls(client: httpx.AsyncClient, domain: str) -> list[str]:
    roots = [
        f"https://www.{domain}/sitemap.xml",
        f"https://{domain}/sitemap.xml",
        f"https://www.{domain}/sitemap_index.xml",
    ]
    seen = set()
    out = []
    queue = roots[:]

    while queue and len(out) < MAX_URLS_PER_DOMAIN:
        sm = queue.pop(0)
        if sm in seen: continue
        seen.add(sm)
        try:
            r = await client.get(sm, timeout=HTTP_TIMEOUT, follow_redirects=True)
            if r.status_code != 200: continue
            soup = BeautifulSoup(r.text, "xml")
            locs = [x.get_text(strip=True) for x in soup.find_all("loc")]
            for u in locs:
                if u.endswith(".xml") and len(seen) < 20:
                    queue.append(u)
                elif looks_relevant(u) and u not in out:
                    out.append(u)
                    if len(out) >= MAX_URLS_PER_DOMAIN: break
        except Exception:
            continue
    return out

async def discover_urls() -> list[str]:
    async with httpx.AsyncClient(headers=HEADERS) as client:
        batches = await asyncio.gather(*(sitemap_urls(client, d) for d in TRUSTED_DOMAINS))
    urls=[]
    seen=set()
    for batch in batches:
        for u in batch:
            if u not in seen:
                seen.add(u); urls.append(u)
    return urls
