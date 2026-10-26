from datetime import timedelta

import pytest
from sqlalchemy import select

from app.models.entities import Execution, Investigation, now
from app.services.workflows import enqueue, reconcile
from app.workers.runner import LostLease, claim, owned


def case_for(db, user):
    reconcile(db, user)
    return db.scalar(select(Investigation))


def test_baseline_not_executed(db, user):
    case = case_for(db, user)
    e = enqueue(db, user, case.id, "baseline", "")
    assert e.status == "not_executed"
    assert claim(db) is None


def test_claim_and_expired_lease_fencing(db, user):
    case = case_for(db, user)
    e = enqueue(db, user, case.id, "ollama", "local-model")
    identifier, first = claim(db)
    assert identifier == e.id
    assert claim(db) is None
    e.lease_until = now() - timedelta(seconds=1)
    db.commit()
    identifier, second = claim(db)
    assert first != second and e.attempts == 2
    with pytest.raises(LostLease):
        owned(db, identifier, first)
    db.rollback()
    assert owned(db, identifier, second).id == e.id


def test_retry_limit(db, user):
    e = enqueue(db, user, case_for(db, user).id, "ollama", "local-model")
    e.attempts = 3
    db.commit()
    assert claim(db) is None
    assert db.get(Execution, e.id).status == "failed"


def test_duplicate_run_rejected(db, user):
    case = case_for(db, user)
    enqueue(db, user, case.id, "ollama", "local-model")
    from fastapi import HTTPException

    with pytest.raises(HTTPException):
        enqueue(db, user, case.id, "ollama", "local-model")
