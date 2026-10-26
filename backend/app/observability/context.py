from contextvars import ContextVar

correlation_id = ContextVar("correlation_id", default=None)
