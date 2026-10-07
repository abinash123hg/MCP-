from backend.utils.safety import evaluate_action

def test_normal_browser_action_allowed():
    result = evaluate_action("open product page")
    assert result.allowed is True
    assert result.requires_approval is False

def test_payment_action_requires_approval():
    result = evaluate_action("place order")
    assert result.allowed is False
    assert result.requires_approval is True

def test_case_and_whitespace_normalization():
    result = evaluate_action("  PAY   NOW ")
    assert result.requires_approval is True
