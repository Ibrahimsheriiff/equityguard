"""
Tests for the evaluation framework itself.
Verifies the evaluator logic works correctly — no agent calls needed.
"""

from src.evaluation.test_cases import EVAL_CASES
from src.safety.financial_guardrails import is_financial_advice_request


def test_eval_cases_exist():
    assert len(EVAL_CASES) > 0

def test_eval_cases_have_required_fields():
    for case in EVAL_CASES:
        assert "name"          in case, f"Missing 'name' in {case}"
        assert "query"         in case, f"Missing 'query' in {case}"
        assert "must_refuse"   in case, f"Missing 'must_refuse' in {case}"
        assert "expected_tools" in case, f"Missing 'expected_tools' in {case}"

def test_refusal_cases_are_correctly_flagged():
    """Every case with must_refuse=True should actually trigger the guardrail."""
    for case in EVAL_CASES:
        if case["must_refuse"]:
            result = is_financial_advice_request(case["query"])
            assert result is True, (
                f"Case '{case['name']}' has must_refuse=True but "
                f"guardrail did not fire for query: '{case['query']}'"
            )

def test_non_refusal_cases_pass_guardrail():
    """Cases with must_refuse=False should not trigger the guardrail."""
    for case in EVAL_CASES:
        if not case["must_refuse"]:
            result = is_financial_advice_request(case["query"])
            assert result is False, (
                f"Case '{case['name']}' should not be refused "
                f"but guardrail fired for: '{case['query']}'"
            )

def test_eval_case_names_are_unique():
    names = [c["name"] for c in EVAL_CASES]
    assert len(names) == len(set(names)), "Duplicate test case names found"

def test_at_least_one_refusal_case():
    refusal_cases = [c for c in EVAL_CASES if c["must_refuse"]]
    assert len(refusal_cases) >= 2, "Need at least 2 refusal test cases"

def test_at_least_one_normal_case():
    normal_cases = [c for c in EVAL_CASES if not c["must_refuse"]]
    assert len(normal_cases) >= 1, "Need at least 1 normal test case"