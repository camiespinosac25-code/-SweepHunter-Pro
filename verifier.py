from __future__ import annotations
import hashlib
from dataclasses import dataclass
from .models import CandidateGiveaway

ALLOWED_BASIC_FIELDS = {"first_name", "last_name", "full_name", "email"}

@dataclass
class VerificationResult:
    score: int
    status: str
    reasons: list[str]

def verify(c: CandidateGiveaway) -> VerificationResult:
    reasons = []
    hard = [
        (c.entry_fee_usd > 0, "Requiere pago"),
        (c.requires_purchase, "No se pudo confirmar participación sin compra"),
        (c.requires_financial_info, "Menciona/solicita datos financieros"),
        (c.requires_ssn, "Menciona/solicita SSN"),
        (c.requires_government_id_at_entry, "Menciona/solicita identificación"),
        (c.requires_third_party_registration, "Requiere pasos u ofertas de terceros"),
        (c.requires_offer_completion, "Requiere completar ofertas"),
        (c.requires_app_install, "Requiere instalar una app"),
        (c.requires_newsletter, "Requiere newsletter"),
        (c.requires_account_creation, "Requiere crear/iniciar cuenta"),
        (not c.rules_verified, "Reglas oficiales no verificadas"),
        (not c.sponsor_domain_verified, "Dominio del patrocinador no confiable"),
        (not c.cross_source_verified, "Falta segunda fuente verificable"),
    ]
    for bad, why in hard:
        if bad: reasons.append(why)

    fields = {x.lower().strip() for x in c.required_fields}
    if not fields.issubset(ALLOWED_BASIC_FIELDS):
        reasons.append("Solicita datos adicionales a nombre/email")

    if reasons:
        return VerificationResult(0, "DESCARTADO", sorted(set(reasons)))
    return VerificationResult(100, "VERIFICADO", [])

def stable_id(c: CandidateGiveaway) -> str:
    raw=f"{c.title}|{c.official_rules_url}".encode()
    return hashlib.sha256(raw).hexdigest()[:24]
