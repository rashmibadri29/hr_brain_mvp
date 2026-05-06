import re

from app.models.ingestion import HRDomain, SensitivityLabel


DOMAIN_KEYWORDS: dict[HRDomain, tuple[str, ...]] = {
    HRDomain.onboarding: ("new hire", "onboarding", "first day", "orientation", "manager", "equipment"),
    HRDomain.benefits: ("benefit", "enrollment", "health plan", "dental", "vision", "401k", "insurance"),
    HRDomain.pto_leave: ("pto", "vacation", "sick leave", "parental leave", "fmla", "leave of absence"),
    HRDomain.payroll: ("payroll", "paycheck", "pay period", "deduction", "tax", "w-2", "direct deposit"),
    HRDomain.compliance: ("compliance", "policy", "legal", "required by law", "audit"),
    HRDomain.offboarding: ("offboarding", "resignation", "termination", "last day", "exit interview"),
    HRDomain.employee_records: ("employee record", "personnel file", "employment verification", "address change"),
    HRDomain.policy_faq: ("faq", "frequently asked", "policy question", "how do i", "what is the process"),
}

SENSITIVITY_KEYWORDS: dict[SensitivityLabel, tuple[str, ...]] = {
    SensitivityLabel.compensation: ("salary", "bonus", "equity", "compensation", "pay rate", "commission"),
    SensitivityLabel.medical_leave: ("medical", "disability", "accommodation", "fmla", "doctor", "diagnosis"),
    SensitivityLabel.employee_relations: ("harassment", "discrimination", "retaliation", "grievance", "investigation"),
}

PII_PATTERN = re.compile(r"\b(?:\d{3}-\d{2}-\d{4}|[\w.+-]+@[\w-]+\.[\w.-]+)\b")


def classify_domain(text: str) -> HRDomain:
    lowered = text.lower()
    scores = {
        domain: sum(1 for keyword in keywords if keyword in lowered)
        for domain, keywords in DOMAIN_KEYWORDS.items()
    }
    best_domain, best_score = max(scores.items(), key=lambda item: item[1])
    return best_domain if best_score > 0 else HRDomain.unknown


def classify_sensitivity(text: str) -> SensitivityLabel:
    lowered = text.lower()
    for label, keywords in SENSITIVITY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return label
    if PII_PATTERN.search(text):
        return SensitivityLabel.pii
    return SensitivityLabel.none


def classify_risk(domain: HRDomain, sensitivity: SensitivityLabel, text: str) -> str:
    lowered = text.lower()
    if sensitivity in {SensitivityLabel.medical_leave, SensitivityLabel.employee_relations}:
        return "high"
    if any(term in lowered for term in ("termination", "legal", "compliance", "compensation dispute")):
        return "high"
    if domain in {HRDomain.payroll, HRDomain.benefits, HRDomain.pto_leave, HRDomain.offboarding}:
        return "medium"
    if sensitivity in {SensitivityLabel.pii, SensitivityLabel.compensation}:
        return "medium"
    return "low"
