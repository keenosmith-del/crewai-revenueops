from fastapi import HTTPException
from sqlalchemy import select


def scoped(db, model, org):
    return select(model).where(model.org_id == org)


def get(db, model, record_id, org, lock=False):
    statement = scoped(db, model, org).where(model.id == record_id)
    if lock:
        statement = statement.with_for_update()
    record = db.scalar(statement)
    if record is None:
        raise HTTPException(404, "Record not found")
    return record


def rows(db, model, org):
    return list(db.scalars(scoped(db, model, org)))
