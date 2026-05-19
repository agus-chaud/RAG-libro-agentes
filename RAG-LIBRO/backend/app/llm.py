"""
Selector de proveedor LLM con cadena de fallback: openrouter → groq → mock.

Usa LangChain `with_fallbacks` ante errores de API, timeout o respuesta vacía.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal, Sequence, Union

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.runnables import Runnable

from app.mock_llm import MockChatModel, MockLLM

Provider = Literal["groq", "openrouter", "mock"]

# Cargar .env desde la raíz del proyecto (RAG-LIBRO/.env)
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")


class RecoverableLLMError(Exception):
    """Error que dispara el siguiente modelo en la cadena de fallback."""


class EmptyResponseError(RecoverableLLMError):
    """El proveedor respondió sin contenido utilizable."""


def _env_provider() -> Provider:
    raw = (os.getenv("LLM_PROVIDER") or "groq").strip().lower()
    if raw in ("groq", "openrouter", "mock"):
        return raw  # type: ignore[return-value]
    return "groq"


def _parse_fallback_chain() -> list[Provider]:
    raw = (
        os.getenv("LLM_FALLBACK_CHAIN") or "openrouter,groq,mock"
    ).strip().lower()
    order: list[Provider] = []
    for part in raw.split(","):
        p = part.strip()
        if p in ("groq", "openrouter", "mock") and p not in order:
            order.append(p)  # type: ignore[arg-type]
    return order or ["openrouter", "groq", "mock"]


def _has_key(name: str) -> bool:
    val = (os.getenv(name) or "").strip()
    return bool(val) and val not in ("your_key_here", "sk-your-****here")


def _request_timeout() -> float:
    try:
        return float(os.getenv("LLM_REQUEST_TIMEOUT", "60"))
    except ValueError:
        return 60.0


def _message_text(message: BaseMessage | str) -> str:
    if isinstance(message, str):
        return message.strip()
    content = message.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        return "".join(parts).strip()
    return str(content or "").strip()


def _is_empty_message(message: BaseMessage | str) -> bool:
    return not _message_text(message)


def _fallback_exceptions() -> tuple[type[BaseException], ...]:
    excs: list[type[BaseException]] = [
        RecoverableLLMError,
        EmptyResponseError,
        TimeoutError,
    ]
    try:
        import httpx

        excs.append(httpx.TimeoutException)
    except ImportError:
        pass
    try:
        from openai import (
            APIConnectionError,
            APIError,
            APITimeoutError,
            AuthenticationError,
            RateLimitError,
        )

        excs.extend(
            [
                RateLimitError,
                APIError,
                APITimeoutError,
                AuthenticationError,
                APIConnectionError,
            ]
        )
    except ImportError:
        pass
    try:
        from groq import APIConnectionError as GroqConn
        from groq import APIError as GroqAPIError
        from groq import APITimeoutError as GroqTimeout
        from groq import RateLimitError as GroqRateLimit

        excs.extend([GroqRateLimit, GroqAPIError, GroqTimeout, GroqConn])
    except ImportError:
        pass
    return tuple(excs)


def _map_to_recoverable(exc: BaseException) -> BaseException:
    if isinstance(exc, RecoverableLLMError):
        return exc
    status = getattr(exc, "status_code", None)
    if status in (429, 402, 500, 502, 503):
        return RecoverableLLMError(str(exc))
    for parent in _fallback_exceptions():
        if isinstance(exc, parent):
            return RecoverableLLMError(str(exc))
    return exc


class ValidatingChatModel(BaseChatModel):
    """Envuelve un chat model y convierte fallos recuperables en excepciones de fallback."""

    delegate: BaseChatModel

    @property
    def _llm_type(self) -> str:
        return f"validating_{self.delegate._llm_type}"

    def _generate(self, messages: list, stop: list[str] | None = None, **kwargs: Any):
        try:
            result = self.delegate._generate(messages, stop=stop, **kwargs)
        except BaseException as exc:
            raise _map_to_recoverable(exc) from exc
        for gen in result.generations:
            if _is_empty_message(gen.message):
                raise EmptyResponseError(
                    f"Respuesta vacía desde {self.delegate._llm_type}"
                )
        return result

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> BaseMessage:
        try:
            out = self.delegate.invoke(input, config=config, **kwargs)
        except BaseException as exc:
            raise _map_to_recoverable(exc) from exc
        if _is_empty_message(out):
            raise EmptyResponseError(f"Respuesta vacía desde {self.delegate._llm_type}")
        return out

    async def ainvoke(self, input: Any, config: Any = None, **kwargs: Any) -> BaseMessage:
        try:
            out = await self.delegate.ainvoke(input, config=config, **kwargs)
        except BaseException as exc:
            raise _map_to_recoverable(exc) from exc
        if _is_empty_message(out):
            raise EmptyResponseError(f"Respuesta vacía desde {self.delegate._llm_type}")
        return out


def _wrap_validated(model: BaseChatModel) -> ValidatingChatModel:
    return ValidatingChatModel(delegate=model)


def _build_openrouter() -> BaseChatModel | None:
    if not _has_key("OPENROUTER_API_KEY"):
        return None
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free"),
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        temperature=0.2,
        timeout=_request_timeout(),
        max_retries=0,
    )


def _build_groq() -> BaseChatModel | None:
    if not _has_key("GROQ_API_KEY"):
        return None
    from langchain_groq import ChatGroq

    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.2,
        timeout=_request_timeout(),
        max_retries=0,
    )


def _build_mock() -> BaseChatModel:
    return MockChatModel()


def _build_provider_model(provider: Provider) -> BaseChatModel | None:
    if provider == "mock":
        return _build_mock()
    if provider == "openrouter":
        return _build_openrouter()
    if provider == "groq":
        return _build_groq()
    return None


def _build_fallback_chain(providers: Sequence[Provider]) -> Runnable:
    models: list[ValidatingChatModel] = []
    for provider in providers:
        built = _build_provider_model(provider)
        if built is not None:
            models.append(_wrap_validated(built))

    if not models:
        models.append(_wrap_validated(_build_mock()))

    primary, *rest = models
    if not rest:
        return primary

    return primary.with_fallbacks(
        rest,
        exceptions_to_handle=_fallback_exceptions(),
    )


def get_llm(provider: Provider | None = None) -> Union[Runnable, BaseChatModel, MockLLM]:
    """
    Devuelve un chat model (o cadena Runnable) listo para LCEL.

    - Sin `provider`: usa `LLM_FALLBACK_CHAIN` (default openrouter,groq,mock).
    - Con `provider`: un solo proveedor (útil en tests).
    """
    if provider is not None:
        built = _build_provider_model(provider)
        if built is None:
            return MockLLM()
        return _wrap_validated(built)

    return _build_fallback_chain(_parse_fallback_chain())


def get_llm_or_mock(provider: Provider | None = None) -> Union[Runnable, BaseChatModel, MockLLM]:
    """Alias para notebooks y tests."""
    return get_llm(provider)
