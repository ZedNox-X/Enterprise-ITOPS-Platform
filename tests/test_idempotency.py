from app.domain.models import AutomationJob


def test_idempotency_key_is_unique() -> None:
    constraint_names = {
        constraint.name for constraint in AutomationJob.__table__.constraints
    }
    assert "uq_automation_idempotency" in constraint_names
