import json

def row_to_api(r):
    f=json.loads(r["raw_flags_json"])
    return {
        "id":r["id"],"title":r["title"],"sponsor":r["sponsor"],
        "prizeDescription":r["prize_description"],"prizeValueUSD":r["prize_value_usd"],
        "entryURL":r["entry_url"],"officialRulesURL":r["official_rules_url"],
        "startDate":r["start_date"],"endDate":r["end_date"],
        "eligibleRegions":json.loads(r["eligible_regions_json"]),
        "minimumAge":r["minimum_age"],"entryMethod":r["entry_method"],
        "requiredFields":json.loads(r["required_fields_json"]),
        "confidenceScore":r["confidence_score"],"status":r["status"],
        "rejectionReasons":json.loads(r["rejection_reasons_json"]),
        "detectedAt":r["detected_at"], **f
    }
