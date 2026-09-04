import json
from datetime import datetime, timezone
from .db import connect
from .verifier import verify, stable_id
from .models import CandidateGiveaway

def save_candidate(c: CandidateGiveaway):
    result = verify(c)
    now = datetime.now(timezone.utc).isoformat()
    gid = stable_id(c)
    flags = {
        "requiresPurchase": c.requires_purchase,
        "entryFeeUSD": c.entry_fee_usd,
        "requiresFinancialInfo": c.requires_financial_info,
        "requiresSSN": c.requires_ssn,
        "requiresGovernmentIDAtEntry": c.requires_government_id_at_entry,
        "requiresThirdPartyRegistration": c.requires_third_party_registration,
        "requiresOfferCompletion": c.requires_offer_completion,
        "requiresAppInstall": c.requires_app_install,
        "requiresNewsletter": c.requires_newsletter,
        "requiresAccountCreation": c.requires_account_creation,
        "sponsorDomainVerified": c.sponsor_domain_verified,
        "rulesVerified": c.rules_verified,
        "crossSourceVerified": c.cross_source_verified,
    }
    with connect() as db:
        db.execute("""
        INSERT INTO giveaways (
          id,title,sponsor,prize_description,prize_value_usd,entry_url,official_rules_url,
          start_date,end_date,eligible_regions_json,minimum_age,entry_method,required_fields_json,
          confidence_score,status,rejection_reasons_json,raw_flags_json,detected_at,updated_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          title=excluded.title,sponsor=excluded.sponsor,prize_description=excluded.prize_description,
          prize_value_usd=excluded.prize_value_usd,entry_url=excluded.entry_url,
          official_rules_url=excluded.official_rules_url,end_date=excluded.end_date,
          confidence_score=excluded.confidence_score,status=excluded.status,
          rejection_reasons_json=excluded.rejection_reasons_json,raw_flags_json=excluded.raw_flags_json,
          updated_at=excluded.updated_at
        """, (
            gid,c.title,c.sponsor,c.prize_description,c.prize_value_usd,str(c.entry_url),
            str(c.official_rules_url),c.start_date.isoformat() if c.start_date else None,
            c.end_date.isoformat() if c.end_date else None,json.dumps(c.eligible_regions),
            c.minimum_age,c.entry_method,json.dumps(c.required_fields),result.score,result.status,
            json.dumps(result.reasons),json.dumps(flags),now,now
        ))
    return gid, result

def list_verified():
    with connect() as db:
        return list(db.execute(
            "SELECT * FROM giveaways WHERE status='VERIFICADO' AND confidence_score>=90 ORDER BY end_date IS NULL, end_date ASC"
        ))

def register_device(token, platform):
    now=datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO devices(token,platform,created_at) VALUES (?,?,?)",
                   (token,platform,now))

def devices_not_notified(giveaway_id):
    with connect() as db:
        return list(db.execute("""
            SELECT d.token FROM devices d
            LEFT JOIN notified n ON n.device_token=d.token AND n.giveaway_id=?
            WHERE n.device_token IS NULL
        """,(giveaway_id,)))

def mark_notified(giveaway_id, token):
    now=datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute("INSERT OR IGNORE INTO notified(giveaway_id,device_token,notified_at) VALUES(?,?,?)",
                   (giveaway_id,token,now))
