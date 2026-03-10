"""HTTP client for the Retsinformation API (retsinformation-api.dk/v1)."""

from __future__ import annotations

from typing import Any

import httpx


class RetsinformationClient:
    """Thin wrapper around the Danish Law Service API."""

    def __init__(self, base_url: str = "https://retsinformation-api.dk/v1") -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=30.0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Perform a GET request and return JSON (or text for markdown)."""
        cleaned: dict[str, Any] = {}
        if params:
            cleaned = {k: v for k, v in params.items() if v is not None}
        resp = self._client.get(path, params=cleaned)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            return resp.json()
        return resp.text

    # ------------------------------------------------------------------
    # Laws
    # ------------------------------------------------------------------

    def search_laws(
        self,
        *,
        search: str | None = None,
        year: int | None = None,
        ressort: str | None = None,
        historical: bool | None = None,
        document_type: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Any:
        """Search / list laws with optional filters."""
        return self._get(
            "/lovgivning/",
            {
                "search": search,
                "year": year,
                "ressort": ressort,
                "historical": historical,
                "document_type": document_type,
                "skip": skip,
                "limit": limit,
            },
        )

    def get_law(self, year: int, number: int, *, include: str | None = None) -> Any:
        """Get a specific law by year and number."""
        return self._get(f"/lovgivning/{year}/{number}", {"include": include})

    def get_law_markdown(
        self,
        year: int,
        number: int,
        *,
        exclude: str | None = None,
        paragraphs: str | None = None,
    ) -> Any:
        """Get a law as markdown text."""
        return self._get(
            f"/lovgivning/{year}/{number}/markdown",
            {"exclude": exclude, "paragraphs": paragraphs},
        )

    def get_law_amendments(
        self, year: int, number: int, *, skip: int = 0, limit: int = 100
    ) -> Any:
        """Get all amendments to a specific law."""
        return self._get(
            f"/lovgivning/{year}/{number}/amendments",
            {"skip": skip, "limit": limit},
        )

    def get_law_versions(
        self, year: int, number: int, *, skip: int = 0, limit: int = 100
    ) -> Any:
        """Get all versions of a law."""
        return self._get(
            f"/lovgivning/{year}/{number}/versions",
            {"skip": skip, "limit": limit},
        )

    def get_latest_law(self, year: int, number: int) -> Any:
        """Get latest version of a law with all amendments applied."""
        return self._get(f"/lovgivning/{year}/{number}/versions/latest")

    def get_latest_law_markdown(
        self,
        year: int,
        number: int,
        *,
        exclude: str | None = None,
        paragraphs: str | None = None,
    ) -> Any:
        """Get latest version of a law as markdown."""
        return self._get(
            f"/lovgivning/{year}/{number}/versions/latest/markdown",
            {"exclude": exclude, "paragraphs": paragraphs},
        )

    def get_law_at_date(self, year: int, number: int, target_date: str) -> Any:
        """Get the law as it was on a specific date."""
        return self._get(f"/lovgivning/{year}/{number}/versions/at/{target_date}")

    def get_law_at_date_markdown(
        self,
        year: int,
        number: int,
        target_date: str,
        *,
        exclude: str | None = None,
        paragraphs: str | None = None,
    ) -> Any:
        """Get the law as it was on a specific date, as markdown."""
        return self._get(
            f"/lovgivning/{year}/{number}/versions/at/{target_date}/markdown",
            {"exclude": exclude, "paragraphs": paragraphs},
        )

    def get_version_diff(self, year: int, number: int, v1: int, v2: int) -> Any:
        """Get diff between two versions of a law."""
        return self._get(f"/lovgivning/{year}/{number}/versions/diff/{v1}/{v2}")

    def get_law_version(self, year: int, number: int, version_number: int) -> Any:
        """Get a specific version of a law."""
        return self._get(
            f"/lovgivning/{year}/{number}/versions/{version_number}"
        )

    def get_law_version_markdown(
        self,
        year: int,
        number: int,
        version_number: int,
        *,
        exclude: str | None = None,
        paragraphs: str | None = None,
    ) -> Any:
        """Get a specific version of a law as markdown."""
        return self._get(
            f"/lovgivning/{year}/{number}/versions/{version_number}/markdown",
            {"exclude": exclude, "paragraphs": paragraphs},
        )

    def get_paragraph(self, year: int, number: int, paragraph: str) -> Any:
        """Get a specific paragraph from the base law."""
        return self._get(f"/lovgivning/{year}/{number}/paragraphs/{paragraph}")

    def get_paragraph_stk(
        self, year: int, number: int, paragraph: str, stk: int
    ) -> Any:
        """Get a specific subsection (stk) from a paragraph."""
        return self._get(
            f"/lovgivning/{year}/{number}/paragraphs/{paragraph}/stk/{stk}"
        )

    def get_law_cases(self, year: int, number: int) -> Any:
        """Get parliamentary cases that led to this enacted law."""
        return self._get(f"/lovgivning/{year}/{number}/cases")

    def get_legislative_history(self, year: int, number: int) -> Any:
        """Get the legislative history for an enacted law."""
        return self._get(f"/lovgivning/{year}/{number}/legislative-history")

    def get_law_actors(self, year: int, number: int) -> Any:
        """Get actors associated with this enacted law."""
        return self._get(f"/lovgivning/{year}/{number}/actors")

    # ------------------------------------------------------------------
    # Bills
    # ------------------------------------------------------------------

    def search_bills(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        periode_id: int | None = None,
        enacted: bool | None = None,
        ressort: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Any:
        """Search / list legislative bills (Lovforslag)."""
        return self._get(
            "/lovgivning/bills/",
            {
                "search": search,
                "status": status,
                "periode_id": periode_id,
                "enacted": enacted,
                "ressort": ressort,
                "skip": skip,
                "limit": limit,
            },
        )

    def get_bill(
        self, number: str, *, periode_id: int | None = None
    ) -> Any:
        """Get a legislative bill by number (e.g. 'L 123' or 'L-123')."""
        return self._get(
            f"/lovgivning/bills/{number}", {"periode_id": periode_id}
        )

    def get_bill_steps(self, number: str) -> Any:
        """Get the legislative process steps for a bill."""
        return self._get(f"/lovgivning/bills/{number}/steps")

    def get_bill_actors(self, number: str) -> Any:
        """Get actors involved in a bill."""
        return self._get(f"/lovgivning/bills/{number}/actors")

    def get_bill_documents(
        self,
        number: str,
        *,
        document_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Any:
        """Get documents related to a bill."""
        return self._get(
            f"/lovgivning/bills/{number}/documents",
            {"document_type": document_type, "skip": skip, "limit": limit},
        )

    def get_bill_text(self, number: str) -> Any:
        """Get all text content from a bill."""
        return self._get(f"/lovgivning/bills/{number}/text")

    def get_bill_keywords(self, number: str) -> Any:
        """Get keywords for a bill."""
        return self._get(f"/lovgivning/bills/{number}/keywords")

    def get_enacted_law(self, number: str) -> Any:
        """Get the enacted law for a bill (if it passed)."""
        return self._get(f"/lovgivning/bills/{number}/enacted-law")

    # ------------------------------------------------------------------
    # Cases
    # ------------------------------------------------------------------

    def search_cases(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        periode_id: int | None = None,
        ressort: str | None = None,
        case_type: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Any:
        """Search all parliamentary case types."""
        return self._get(
            "/lovgivning/cases/",
            {
                "search": search,
                "status": status,
                "periode_id": periode_id,
                "ressort": ressort,
                "case_type": case_type,
                "skip": skip,
                "limit": limit,
            },
        )

    def get_case(self, ft_id: int) -> Any:
        """Get a case by FT API ID."""
        return self._get(f"/lovgivning/cases/{ft_id}")

    def get_case_steps(self, ft_id: int) -> Any:
        """Get legislative process steps for a case."""
        return self._get(f"/lovgivning/cases/{ft_id}/steps")

    def get_case_actors(self, ft_id: int) -> Any:
        """Get actors involved in a case."""
        return self._get(f"/lovgivning/cases/{ft_id}/actors")

    def get_case_documents(
        self,
        ft_id: int,
        *,
        document_type: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Any:
        """Get documents for a case."""
        return self._get(
            f"/lovgivning/cases/{ft_id}/documents",
            {"document_type": document_type, "skip": skip, "limit": limit},
        )

    def get_case_keywords(self, ft_id: int) -> Any:
        """Get keywords for a case."""
        return self._get(f"/lovgivning/cases/{ft_id}/keywords")

    def get_case_text(self, ft_id: int) -> Any:
        """Get all text content from a case."""
        return self._get(f"/lovgivning/cases/{ft_id}/text")

    # ------------------------------------------------------------------
    # Actors
    # ------------------------------------------------------------------

    def search_actors(
        self,
        *,
        search: str | None = None,
        actor_type: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Any:
        """Search actors (persons, committees, ministries, parties)."""
        return self._get(
            "/lovgivning/actors/",
            {
                "search": search,
                "actor_type": actor_type,
                "skip": skip,
                "limit": limit,
            },
        )

    def get_actor(self, ft_id: int) -> Any:
        """Get an actor by FT API ID."""
        return self._get(f"/lovgivning/actors/{ft_id}")

    def get_actor_memberships(
        self, ft_id: int, *, active_only: bool = False
    ) -> Any:
        """Get party and committee memberships for an actor."""
        return self._get(
            f"/lovgivning/actors/{ft_id}/memberships",
            {"active_only": active_only},
        )

    def get_actor_relationships(
        self, ft_id: int, *, skip: int = 0, limit: int = 100
    ) -> Any:
        """Get relationships for an actor."""
        return self._get(
            f"/lovgivning/actors/{ft_id}/relationships",
            {"skip": skip, "limit": limit},
        )

    # ------------------------------------------------------------------
    # Keywords
    # ------------------------------------------------------------------

    def search_keywords(
        self,
        *,
        search: str | None = None,
        keyword_type: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Any:
        """Search keywords (Emneord)."""
        return self._get(
            "/lovgivning/keywords/",
            {
                "search": search,
                "keyword_type": keyword_type,
                "skip": skip,
                "limit": limit,
            },
        )

    def get_keyword(self, ft_id: int) -> Any:
        """Get a keyword by FT API ID."""
        return self._get(f"/lovgivning/keywords/{ft_id}")

    def get_cases_for_keyword(
        self, ft_id: int, *, skip: int = 0, limit: int = 100
    ) -> Any:
        """Get all cases tagged with a specific keyword."""
        return self._get(
            f"/lovgivning/keywords/{ft_id}/cases",
            {"skip": skip, "limit": limit},
        )

    # ------------------------------------------------------------------
    # Periods
    # ------------------------------------------------------------------

    def get_periods(
        self,
        *,
        type_filter: str | None = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> Any:
        """List parliamentary periods."""
        return self._get(
            "/lovgivning/perioder/",
            {
                "type_filter": type_filter,
                "active_only": active_only,
                "skip": skip,
                "limit": limit,
            },
        )

    def get_current_period(self) -> Any:
        """Get the current parliamentary period."""
        return self._get("/lovgivning/perioder/current")

    def get_period(self, ft_id: int) -> Any:
        """Get a parliamentary period by FT API ID."""
        return self._get(f"/lovgivning/perioder/{ft_id}")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._client.close()
