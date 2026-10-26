from app.agents.schemas.outputs import Findings


def validate_findings(value, context):
    result = value if isinstance(value, Findings) else Findings.model_validate(value)
    if (
        result.investigation_id != context["investigation_id"]
        or result.transaction_id != context["transaction_id"]
        or result.currency != context["currency"]
    ):
        raise ValueError("Output identity/currency does not match the case")
    for citation in result.evidence:
        record = context["records"].get(citation.reference)
        if (
            record is None
            or citation.field not in record
            or record[citation.field] != citation.value
        ):
            raise ValueError("Citation does not exactly match authoritative evidence")
    invoice_ids = {key.split(":", 1)[1] for key in context["records"] if key.startswith("invoice:")}
    for allocation in result.allocations:
        if allocation.invoice_id not in invoice_ids:
            raise ValueError("Invented or out-of-scope invoice")
        if not any(e.reference == f"invoice:{allocation.invoice_id}" for e in result.evidence):
            raise ValueError("Every proposed invoice requires cited evidence")
    if result.allocations and result.recommendation != "propose_allocation":
        raise ValueError("Contradictory recommendation and allocations")
    if result.recommendation == "propose_allocation" and not result.allocations:
        raise ValueError("Allocation recommendation has no allocation")
    return result


def guardrail(context, record_validation=None):
    def check(output):
        try:
            result = validate_findings(
                output.pydantic or Findings.model_validate_json(output.raw), context
            )
            if record_validation:
                record_validation("accepted", None)
            return True, result.model_dump_json()
        except (ValueError, TypeError) as exc:
            if record_validation:
                record_validation("rejected", type(exc).__name__)
            return False, str(exc)

    return check
