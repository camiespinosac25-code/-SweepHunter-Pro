from __future__ import annotations
import os, time, jwt, httpx
from .config import APNS_TEAM_ID, APNS_KEY_ID, APNS_BUNDLE_ID, APNS_PRIVATE_KEY_PATH, APNS_USE_SANDBOX

def configured():
    return all([APNS_TEAM_ID, APNS_KEY_ID, APNS_BUNDLE_ID, APNS_PRIVATE_KEY_PATH])

def _token():
    key=open(APNS_PRIVATE_KEY_PATH, "r", encoding="utf-8").read()
    return jwt.encode(
        {"iss": APNS_TEAM_ID, "iat": int(time.time())},
        key, algorithm="ES256", headers={"kid": APNS_KEY_ID}
    )

async def send(token: str, title: str, body: str, giveaway_id: str) -> bool:
    if not configured():
        return False
    host = "https://api.sandbox.push.apple.com" if APNS_USE_SANDBOX else "https://api.push.apple.com"
    url=f"{host}/3/device/{token}"
    payload={"aps":{"alert":{"title":title,"body":body},"sound":"default"},"giveaway_id":giveaway_id}
    headers={
        "authorization": f"bearer {_token()}",
        "apns-topic": APNS_BUNDLE_ID,
        "apns-push-type":"alert",
        "apns-priority":"10",
    }
    async with httpx.AsyncClient(http2=True, timeout=15) as c:
        r=await c.post(url, json=payload, headers=headers)
    return 200 <= r.status_code < 300
