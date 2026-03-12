"""Dispatches Azure OpenAI tool calls to the Retsinformation API client."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from retschat.api_client import RetsinformationClient
from retschat.config import Settings

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Maps tool names → API client methods, executes, and returns JSON strings."""

    def __init__(self, client: RetsinformationClient, settings: Settings) -> None:
        self.client = client
        self.max_chars = settings.max_tool_response_chars

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool call and return a JSON string for the LLM."""
        handler = getattr(self, f"_handle_{tool_name}", None)
        if handler is None:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        try:
            result = handler(**arguments)
            return self._truncate(self._serialize(result))
        except httpx.HTTPStatusError as exc:
            logger.warning("API error for %s: %s", tool_name, exc)
            return json.dumps({
                "error": f"API returned {exc.response.status_code}",
                "detail": exc.response.text[:500],
            })
        except Exception as exc:
            logger.exception("Tool execution error for %s", tool_name)
            return json.dumps({"error": str(exc)})

    # ------------------------------------------------------------------
    # Serialization / truncation
    # ------------------------------------------------------------------

    @staticmethod
    def _serialize(obj: Any) -> str:
        if isinstance(obj, str):
            return obj
        return json.dumps(obj, ensure_ascii=False, default=str)

    def _truncate(self, text: str) -> str:
        if len(text) <= self.max_chars:
            return text
        return text[: self.max_chars] + "\n\n... [truncated – ask for specific paragraphs or narrower filters]"

    # ------------------------------------------------------------------
    # Law handlers
    # ------------------------------------------------------------------

    def _handle_search_laws(self, **kwargs: Any) -> Any:
        return self.client.search_laws(**kwargs)

    def _handle_get_law_text(
        self,
        year: int,
        number: int,
        version: str = "latest",
        target_date: str | None = None,
        version_number: int | None = None,
        paragraphs: str | None = None,
        exclude: str | None = None,
    ) -> Any:
        md_kwargs: dict[str, Any] = {"exclude": exclude, "paragraphs": paragraphs}
        if version == "original":
            return self.client.get_law_markdown(year, number, **md_kwargs)
        if version == "at_date" and target_date:
            return self.client.get_law_at_date_markdown(
                year, number, target_date, **md_kwargs
            )
        if version == "specific" and version_number is not None:
            return self.client.get_law_version_markdown(
                year, number, version_number, **md_kwargs
            )
        # default: latest
        return self.client.get_latest_law_markdown(year, number, **md_kwargs)

    def _handle_get_law_paragraph(
        self,
        year: int,
        number: int,
        paragraph: str,
        stk: int | None = None,
    ) -> Any:
        if stk is not None:
            return self.client.get_paragraph_stk(year, number, paragraph, stk)
        return self.client.get_paragraph(year, number, paragraph)

    def _handle_get_law_metadata(
        self, year: int, number: int, include: str | None = None
    ) -> Any:
        return self.client.get_law(year, number, include=include)

    def _handle_get_law_amendments(self, year: int, number: int) -> Any:
        return self.client.get_law_amendments(year, number)

    def _handle_get_law_versions(self, year: int, number: int) -> Any:
        return self.client.get_law_versions(year, number)

    def _handle_compare_law_versions(
        self, year: int, number: int, v1: int, v2: int
    ) -> Any:
        return self.client.get_version_diff(year, number, v1, v2)

    def _handle_get_legislative_history(self, year: int, number: int) -> Any:
        return self.client.get_legislative_history(year, number)

    def _handle_get_law_actors(self, year: int, number: int) -> Any:
        return self.client.get_law_actors(year, number)

    # ------------------------------------------------------------------
    # Bill handlers
    # ------------------------------------------------------------------

    def _handle_search_bills(self, **kwargs: Any) -> Any:
        return self.client.search_bills(**kwargs)

    def _handle_get_bill_details(
        self, number: str, include_text: bool = False, include_keywords: bool = False, include_enacted_law: bool = False
    ) -> Any:
        bill = self.client.get_bill(number)
        if include_text:
            try:
                text = self.client.get_bill_text(number)
                bill["_text_content"] = text
            except Exception:
                pass
        if include_keywords:
            try:
                keywords = self.client.get_bill_keywords(number)
                bill["_keywords"] = keywords
            except Exception:
                pass
        if include_enacted_law:
            try:
                enacted = self.client.get_enacted_law(number)
                bill["_enacted_law"] = enacted
            except Exception:
                pass
        return bill

    def _handle_get_bill_lifecycle(self, number: str) -> Any:
        return self.client.get_bill_steps(number)

    def _handle_get_bill_actors(self, number: str) -> Any:
        return self.client.get_bill_actors(number)

    def _handle_get_bill_documents(
        self, number: str, document_type: str | None = None
    ) -> Any:
        return self.client.get_bill_documents(number, document_type=document_type)

    def _handle_get_bill_document_files(self, number: str, doc_ft_id: int) -> Any:
        return self.client.get_bill_document_files(number, doc_ft_id)

    # ------------------------------------------------------------------
    # Case handlers
    # ------------------------------------------------------------------

    def _handle_search_cases(self, **kwargs: Any) -> Any:
        return self.client.search_cases(**kwargs)

    def _handle_get_case_details(self, ft_id: int, include_text: bool = False, include_keywords: bool = False) -> Any:
        case = self.client.get_case(ft_id)
        if include_text:
            try:
                text = self.client.get_case_text(ft_id)
                case["_text_content"] = text
            except Exception:
                pass
        if include_keywords:
            try:
                keywords = self.client.get_case_keywords(ft_id)
                case["_keywords"] = keywords
            except Exception:
                pass
        return case

    def _handle_get_case_lifecycle(self, ft_id: int) -> Any:
        return self.client.get_case_steps(ft_id)

    def _handle_get_case_actors(self, ft_id: int) -> Any:
        return self.client.get_case_actors(ft_id)

    def _handle_get_case_documents(
        self, ft_id: int, document_type: str | None = None
    ) -> Any:
        return self.client.get_case_documents(ft_id, document_type=document_type)

    # ------------------------------------------------------------------
    # Actor handlers
    # ------------------------------------------------------------------

    def _handle_search_actors(self, **kwargs: Any) -> Any:
        return self.client.search_actors(**kwargs)

    def _handle_get_actor_details(
        self, ft_id: int, include_memberships: bool = False, include_relationships: bool = False
    ) -> Any:
        actor = self.client.get_actor(ft_id)
        if include_memberships:
            try:
                memberships = self.client.get_actor_memberships(ft_id)
                actor["_memberships"] = memberships
            except Exception:
                pass
        if include_relationships:
            try:
                relationships = self.client.get_actor_relationships(ft_id)
                actor["_relationships"] = relationships
            except Exception:
                pass
        return actor

    # ------------------------------------------------------------------
    # Keyword handlers
    # ------------------------------------------------------------------

    def _handle_search_keywords(self, **kwargs: Any) -> Any:
        return self.client.search_keywords(**kwargs)

    def _handle_get_cases_for_keyword(self, ft_id: int, **kwargs: Any) -> Any:
        return self.client.get_cases_for_keyword(ft_id, **kwargs)

    # ------------------------------------------------------------------
    # Period handlers
    # ------------------------------------------------------------------

    def _handle_get_current_period(self) -> Any:
        return self.client.get_current_period()

    def _handle_get_periods(self, **kwargs: Any) -> Any:
        return self.client.get_periods(**kwargs)
