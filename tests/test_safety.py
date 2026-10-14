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
    assert result.allowed is False


def test_buy_now_blocked():
    result = evaluate_action("click Buy Now button")
    assert result.allowed is False
    assert result.requires_approval is True


def test_fill_normal_allowed():
    result = evaluate_action('fill #search "wireless headphones"')
    assert result.allowed is True


def test_security_abuse_blocked():
    result = evaluate_action("bypass captcha on login")
    assert result.allowed is False
