from pathlib import Path

from onboarding_copilot.agent import answer_question, build_context
from onboarding_copilot.orientation import build_orientation
from onboarding_copilot.profiler import find_relationships, load_dataset, profile_dataset
from onboarding_copilot.sensitivity import classify_column, redact, scan_text

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample"


def _profiles():
    profiles = profile_dataset(load_dataset(SAMPLE))
    return profiles, find_relationships(profiles)


def test_column_name_rules():
    assert "email" in classify_column("email")
    assert "salary" in classify_column("annual_salary")
    assert "person_name" in classify_column("first_name")
    assert classify_column("product_name") == []


def test_value_rules_catch_secrets_in_text():
    text = "my key is sk-abcdefghijklmnopqrstuv and ssn 912-34-5678"
    kinds = {f.kind for f in scan_text(text)}
    assert {"api_key", "ssn"} <= kinds
    cleaned = redact(text)
    assert "sk-abcdef" not in cleaned and "912-34-5678" not in cleaned


def test_profiler_finds_expected_joins_and_sensitive_columns():
    profiles, rels = _profiles()
    assert ("customers", "orders", "customer_id") in rels
    assert ("orders", "products", "product_id") in rels
    employees = profiles["employees"]
    assert employees.column("salary").sensitive_kinds
    assert employees.column("ssn").sensitive_kinds


def test_context_masks_sensitive_samples():
    profiles, rels = _profiles()
    context = build_context(profiles, rels)
    ssn_sample = profiles["employees"].column("ssn").samples[0]
    assert ssn_sample not in context
    assert "employees.ssn" in context and "SENSITIVE" in context


def test_orientation_has_questions_and_sensitive_fields():
    profiles, rels = _profiles()
    orientation = build_orientation(profiles, rels)
    assert orientation.starter_questions
    assert any(t == "employees" for t, _, _ in orientation.sensitive_fields)


def test_offline_answer_cites_columns_and_flags_pasted_secrets(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    profiles, rels = _profiles()
    result = answer_question("What is in the orders status column? my ssn is 912-34-5678", profiles, rels)
    assert result.mode == "offline"
    assert "[orders.status]" in result.text
    assert any(f.kind == "ssn" for f in result.flags)
    assert "912-34-5678" not in result.redacted_question


def test_live_mode_sends_only_redacted_question():
    class FakeBlock:
        type = "text"
        text = "Orders join to customers on customer_id [orders.customer_id]."

    class FakeClient:
        def __init__(self):
            self.sent = None
            self.messages = self

        def create(self, **kwargs):
            self.sent = kwargs
            return type("R", (), {"content": [FakeBlock()]})()

    profiles, rels = _profiles()
    client = FakeClient()
    result = answer_question("How do orders link? ssn 912-34-5678", profiles, rels, client=client)
    assert result.mode == "live"
    sent = client.sent["messages"][0]["content"]
    assert "912-34-5678" not in sent
