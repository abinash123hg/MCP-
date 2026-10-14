from dataclasses import dataclass

# Phrases that indicate irreversible financial or high-risk side effects.
IRREVERSIBLE_TERMS = {
    "place order",
    "buy now",
    "pay now",
    "submit payment",
    "confirm payment",
    "complete purchase",
    "finalize purchase",
    "send money",
    "transfer money",
    "checkout and pay",
    "confirm order",
    "place your order",
    "complete order",
    "pay with",
    "submit order",
}

# Extra high-risk patterns (credentials / security bypass).
BLOCKED_TERMS = {
    "bypass captcha",
    "solve captcha",
    "steal password",
    "extract cookie",
    "steal cookie",
    "dump session",
}


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    requires_approval: bool
    reason: str


def evaluate_action(action: str) -> SafetyDecision:
    """Decide whether an agent/MCP action is allowed without human approval."""
    normalized = " ".join(action.lower().strip().split())

    if any(term in normalized for term in BLOCKED_TERMS):
        return SafetyDecision(
            False,
            True,
            "Security-sensitive or abuse-oriented action is blocked.",
        )

    if any(term in normalized for term in IRREVERSIBLE_TERMS):
        return SafetyDecision(
            False,
            True,
            "Irreversible purchase/payment action requires explicit human approval.",
        )

    return SafetyDecision(
        True,
        False,
        "Read-only or reversible browser action is allowed.",
    )
