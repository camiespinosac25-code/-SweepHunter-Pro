from __future__ import annotations
import httpx
from .discovery import discover_urls, HEADERS
from .parser import extract_candidate
from .corroborator import corroborate
from .repository import save_candidate, devices_not_notified, mark_notified
from .apns import send

async def scan_once():
    urls = await discover_urls()
    stats={"discovered":len(urls),"parsed":0,"verified":0,"rejected":0,"errors":0}
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True, timeout=18) as client:
        for url in urls:
            try:
                r=await client.get(url)
                if r.status_code != 200: continue
                c=extract_candidate(str(r.url), r.text)
                if not c: continue
                stats["parsed"] += 1

                # Require a truly separate source.
                c.cross_source_verified = await corroborate(c.title, str(c.official_rules_url))
                gid, result = save_candidate(c)
                if result.status == "VERIFICADO":
                    stats["verified"] += 1
                    for row in devices_not_notified(gid):
                        token=row["token"]
                        ok=await send(token, "Sorteo verificado", c.title, gid)
                        if ok: mark_notified(gid, token)
                else:
                    stats["rejected"] += 1
            except Exception:
                stats["errors"] += 1
    return stats
