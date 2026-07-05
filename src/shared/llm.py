"""Chat-model factory with a deterministic offline fallback.

``get_chat_model()`` returns a real ``ChatOpenAI`` when ``OPENAI_API_KEY`` is set,
otherwise a :class:`FakeToolCallingModel`. The fake is not a toy stub: it supports
``bind_tools`` (emitting real tool calls so agent loops actually execute) and
``with_structured_output`` (returning populated Pydantic objects). This lets every
advanced module run — and be tested — with zero credentials, while the exact same
code talks to OpenAI once a key is present.
"""

from __future__ import annotations

from typing import Any, Sequence

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import BaseModel, ConfigDict

from src.shared.config import get_settings


def _tool_name(tool: Any) -> str:
    """Extract a tool name from a BaseTool, dict schema, or plain callable."""
    if isinstance(tool, dict):
        return tool.get("name") or tool.get("function", {}).get("name", "tool")
    return getattr(tool, "name", getattr(tool, "__name__", "tool"))


def _sample_value(annotation: Any, text: str, field_name: str) -> Any:
    """Deterministically fabricate a value of ``annotation`` from ``text``.

    Used by the offline fake for tool arguments and structured output. Kept
    intentionally simple: demo schemas use flat, primitive fields.
    """
    if annotation in (str, None) or annotation is str:
        return text or field_name
    if annotation is int:
        return 1
    if annotation is float:
        return 1.0
    if annotation is bool:
        return True
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return _build_model(annotation, text)
    # list / dict / Optional / unknown -> safe defaults
    origin = getattr(annotation, "__origin__", None)
    if origin in (list, set, tuple):
        return []
    if origin is dict:
        return {}
    return text or field_name


def _build_model(schema: type[BaseModel], text: str) -> BaseModel:
    """Instantiate ``schema`` by sampling a value for each field from ``text``."""
    values: dict[str, Any] = {}
    for name, field in schema.model_fields.items():
        values[name] = _sample_value(field.annotation, text, name)
    return schema(**values)


class FakeToolCallingModel(BaseChatModel):
    """A deterministic, offline chat model.

    Behaviour:

    - With bound tools and budget remaining, it emits a tool call for the tool
      whose name best matches the latest human message (falling back to the first
      unused tool once, to demonstrate the loop).
    - Otherwise it returns a final text answer — either the next canned response
      or a synthesis of observed ``ToolMessage`` results.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    responses: list[str] = []
    bound_tools: list[Any] = []
    max_tool_calls: int = 2

    @property
    def _llm_type(self) -> str:
        return "fake-tool-calling"

    # -- tool binding -------------------------------------------------------
    def bind_tools(self, tools: Sequence[Any], **kwargs: Any) -> BaseChatModel:
        """Return a copy of this model that will call ``tools``."""
        return self.model_copy(update={"bound_tools": list(tools)})

    def with_structured_output(  # type: ignore[override]
        self, schema: type[BaseModel], **kwargs: Any
    ) -> Runnable:
        """Return a runnable that produces a populated ``schema`` instance."""

        def _run(model_input: Any) -> BaseModel:
            return _build_model(schema, _latest_human_text(_as_messages(model_input)))

        return RunnableLambda(_run)

    # -- generation ---------------------------------------------------------
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=self._respond(messages))])

    def _respond(self, messages: list[BaseMessage]) -> AIMessage:
        names = [_tool_name(t) for t in self.bound_tools]
        prior = [
            tc["name"]
            for m in messages
            if isinstance(m, AIMessage)
            for tc in (m.tool_calls or [])
        ]
        query = _latest_human_text(messages)

        if names and len(prior) < self.max_tool_calls:
            selected = self._select_tool(query, names, set(prior))
            if selected is not None:
                return AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": selected,
                            "args": self._make_args(selected, query),
                            "id": f"call_{len(prior) + 1}",
                            "type": "tool_call",
                        }
                    ],
                )
        return AIMessage(content=self._final_text(messages, query))

    def _select_tool(self, query: str, names: list[str], used: set[str]) -> str | None:
        q = query.lower()
        matches = [
            n
            for n in names
            if n not in used and any(tok in q for tok in n.lower().split("_"))
        ]
        if matches:
            return matches[0]
        unused = [n for n in names if n not in used]
        if not used and unused:  # kick off the loop with the first tool
            return unused[0]
        return None

    def _make_args(self, tool_name: str, query: str) -> dict[str, Any]:
        tool = next((t for t in self.bound_tools if _tool_name(t) == tool_name), None)
        schema = getattr(tool, "args_schema", None)
        if schema is None or not hasattr(schema, "model_fields"):
            return {"query": query}
        return {
            name: _sample_value(field.annotation, query, name)
            for name, field in schema.model_fields.items()
        }

    def _final_text(self, messages: list[BaseMessage], query: str) -> str:
        if self.responses:
            human_turns = sum(1 for m in messages if isinstance(m, HumanMessage))
            return self.responses[(max(human_turns, 1) - 1) % len(self.responses)]
        observations = [str(m.content) for m in messages if isinstance(m, ToolMessage)]
        if observations:
            return "[offline] Completed using tools. Observations: " + " | ".join(
                observations
            )
        return f"[offline] Echo: {query}"


def _as_messages(model_input: Any) -> list[BaseMessage]:
    """Coerce arbitrary runnable input into a message list."""
    if isinstance(model_input, BaseMessage):
        return [model_input]
    if isinstance(model_input, str):
        return [HumanMessage(content=model_input)]
    if isinstance(model_input, dict) and "messages" in model_input:
        return list(model_input["messages"])
    if isinstance(model_input, (list, tuple)):
        out: list[BaseMessage] = []
        for item in model_input:
            out.extend(_as_messages(item))
        return out
    return [HumanMessage(content=str(model_input))]


def _latest_human_text(messages: list[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return str(messages[-1].content) if messages else ""


def get_chat_model(
    *,
    temperature: float | None = None,
    responses: list[str] | None = None,
    max_tool_calls: int = 2,
    **kwargs: Any,
) -> BaseChatModel:
    """Return a chat model: real ``ChatOpenAI`` if configured, else the fake.

    ``responses`` seeds the offline fake with canned final answers so a demo has
    stable, meaningful output.
    """
    settings = get_settings()
    if settings.has_openai():
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature if temperature is None else temperature,
            **kwargs,
        )
    return FakeToolCallingModel(
        responses=responses or [], max_tool_calls=max_tool_calls
    )


def is_offline() -> bool:
    """True when no real LLM backend is configured."""
    return not get_settings().has_openai()
