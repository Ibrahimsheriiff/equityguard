"""
Tests for financial guardrails.
These run without any API calls — pure logic tests.
"""

from src.safety.financial_guardrails import is_financial_advice_request, refusal_message


def test_should_buy_is_refused():
    assert is_financial_advice_request("should I buy CBA.AX today?") is True

def test_should_sell_is_refused():
    assert is_financial_advice_request("should I sell my NVDA shares?") is True

def test_make_money_is_refused():
    assert is_financial_advice_request("tell me what to invest in to make money") is True

def test_guaranteed_profit_is_refused():
    assert is_financial_advice_request("which stock gives guaranteed profit?") is True

def test_risk_analysis_is_allowed():
    assert is_financial_advice_request("assess the risk of CBA.AX") is False

def test_how_risky_is_allowed():
    assert is_financial_advice_request("how risky is NVDA right now?") is False

def test_price_question_is_allowed():
    assert is_financial_advice_request("what is the current price of AAPL?") is False

def test_refusal_message_is_not_empty():
    msg = refusal_message()
    assert isinstance(msg, str)
    assert len(msg) > 20

def test_case_insensitive():
    assert is_financial_advice_request("SHOULD I BUY CBA.AX?") is True
    assert is_financial_advice_request("Should I Sell TSLA?") is True