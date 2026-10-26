from urllib.parse import urlparse

import httpx

from app.core.config import settings


def health():
    if settings.model_mode == "baseline":
        return {"status": "not_executed", "reason": "Baseline mode"}
    if settings.model_mode == "hosted":
        return {
            "status": "configured"
            if settings.hosted_enabled and settings.hosted_model
            else "disabled",
            "live_verified": False,
        }
    endpoint = urlparse(settings.ollama_url)
    if endpoint.scheme != "http" or endpoint.hostname not in (
        "localhost",
        "127.0.0.1",
        "host.docker.internal",
        "ollama",
    ):
        raise ValueError("Local inference endpoint must be a permitted local host")
    with httpx.Client(timeout=5) as client:
        response = client.get(settings.ollama_url + "/api/tags")
        response.raise_for_status()
        names = [m["name"] for m in response.json()["models"]]
        if settings.ollama_model not in names:
            raise ValueError("Configured Ollama model not installed")
        details = client.post(
            settings.ollama_url + "/api/show", json={"model": settings.ollama_model}
        )
        details.raise_for_status()
        capabilities = details.json().get("capabilities", [])
        if "tools" not in capabilities:
            raise ValueError("Configured model does not advertise tool support")
    return {"status": "available", "capabilities": capabilities, "model": settings.ollama_model}


def get_llm():
    from crewai import LLM

    if settings.model_mode == "ollama":
        health()
        return LLM(
            model="openai/" + settings.ollama_model,
            base_url=settings.ollama_url.rstrip("/") + "/v1",
            api_key="ollama",
            temperature=0,
            timeout=90,
            max_tokens=2500,
        )
    if settings.model_mode == "hosted" and settings.hosted_enabled and settings.hosted_model:
        return LLM(model=settings.hosted_model, timeout=90, max_tokens=2500)
    raise RuntimeError("No authorised model provider; inference not executed")
