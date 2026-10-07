from dataclasses import dataclass

IRREVERSIBLE_TERMS = {
    "place order", "buy now", "pay now", "submit payment", "confirm payment",
    "complete purchase", "finalize purchase", "send money", "transfer money"
}

@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    requires_approval: bool
    reason: str

def evaluate_action(action: str) -> SafetyDecision:
    normalized = " ".join(action.lower().strip().split())
    if any(term in normalized for term in IRREVERSIBLE_TERMS):
        return SafetyDecision(False, True, "Irreversible purchase/payment action requires explicit human approval.")
    return SafetyDecision(True, False, "Read-only or reversible browser action is allowed.")
