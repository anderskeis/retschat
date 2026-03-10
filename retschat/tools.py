"""Azure OpenAI function-calling tool definitions for the Retsinformation API."""

from __future__ import annotations

TOOLS: list[dict] = [
    # ------------------------------------------------------------------
    # Laws
    # ------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_laws",
            "description": (
                "Search and list Danish laws and regulations from retsinformation.dk. "
                "Use this when the user asks to find laws by topic, year, ministry (ressort), "
                "or document type.  Returns a paginated list with title, year, number, and metadata. "
                "Document types include LOVH (original law), LBKH (consolidated act), BEK (executive order), etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Free-text search in law titles (e.g. 'straffelov', 'lejelov', 'sundhed').",
                    },
                    "year": {
                        "type": "integer",
                        "description": "Filter by the year the law was published.",
                    },
                    "ressort": {
                        "type": "string",
                        "description": "Filter by responsible ministry, e.g. 'Justitsministeriet', 'Sundhedsministeriet'.",
                    },
                    "historical": {
                        "type": "boolean",
                        "description": "true = only historical (superseded) laws, false = only current laws.",
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Filter by document type code: LOVH, LBKH, BEK, CIR, VEJ, etc.",
                    },
                    "skip": {"type": "integer", "description": "Pagination offset (default 0)."},
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return (default 20, max 100).",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_law_text",
            "description": (
                "Get the full text of a Danish law as readable markdown. "
                "Use this when the user wants to read a specific law or parts of it. "
                "You can get the original version, the latest consolidated version, or the version at a specific date. "
                "You can also filter to specific paragraphs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year (e.g. 2025)."},
                    "number": {"type": "integer", "description": "The law's number (e.g. 468)."},
                    "version": {
                        "type": "string",
                        "enum": ["original", "latest", "at_date"],
                        "description": (
                            "'original' = base law (version 1), "
                            "'latest' = most recent with all amendments, "
                            "'at_date' = law as it was on target_date."
                        ),
                    },
                    "target_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (only used when version='at_date').",
                    },
                    "paragraphs": {
                        "type": "string",
                        "description": "Paragraph filter: '1-5' for range, '10,15,20' for specific paragraphs.",
                    },
                    "exclude": {
                        "type": "string",
                        "description": "Comma-separated sections to exclude: 'preamble', 'signature', 'appendices', 'case_history'.",
                    },
                },
                "required": ["year", "number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_law_paragraph",
            "description": (
                "Get a specific paragraph (§) from a law, optionally a specific subsection (stk.). "
                "Use when the user refers to a specific paragraph number like '§ 15' or '§ 15, stk. 2'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                    "paragraph": {
                        "type": "string",
                        "description": "Paragraph number (e.g. '1', '15', '15a').",
                    },
                    "stk": {
                        "type": "integer",
                        "description": "Subsection number (stk.), 1-indexed. Omit to get the entire paragraph.",
                    },
                },
                "required": ["year", "number", "paragraph"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_law_metadata",
            "description": (
                "Get metadata about a law: title, ministry, document type, effective dates, "
                "paragraph/chapter counts, case history.  Use when the user asks about details of a law "
                "without needing the full text. Also supports ?include=case,actors,timeline,full for FT ODA data."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                    "include": {
                        "type": "string",
                        "description": "Comma-separated FT ODA data to include: 'case', 'actors', 'timeline', 'full'.",
                    },
                },
                "required": ["year", "number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_law_amendments",
            "description": (
                "Get all amendments to a specific law. Returns the list of amending laws "
                "and the paragraph content of each amendment."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                },
                "required": ["year", "number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_law_versions",
            "description": (
                "Get all historical versions of a law. Each version represents the law "
                "after an amendment was applied. Returns version numbers and effective dates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                },
                "required": ["year", "number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_law_versions",
            "description": (
                "Get a diff between two versions of a law, showing what changed. "
                "Use when the user asks what changed between version X and Y, or what a specific amendment changed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                    "v1": {"type": "integer", "description": "First version number (typically the earlier version)."},
                    "v2": {"type": "integer", "description": "Second version number (typically the later version)."},
                },
                "required": ["year", "number", "v1", "v2"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_legislative_history",
            "description": (
                "Get the full legislative history for an enacted law: the parliamentary case (Lovforslag), "
                "all process steps, link to ft.dk. Use when the user asks about the legislative process, "
                "who proposed a law, or when it was debated."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                },
                "required": ["year", "number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_law_actors",
            "description": (
                "Get actors (sponsors, ministers, spokespeople, committees) associated with a specific enacted law."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "year": {"type": "integer", "description": "The law's year."},
                    "number": {"type": "integer", "description": "The law's number."},
                },
                "required": ["year", "number"],
            },
        },
    },
    # ------------------------------------------------------------------
    # Bills
    # ------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_bills",
            "description": (
                "Search legislative bills (Lovforslag) from the Danish Parliament. "
                "Filter by title, status (Vedtaget/Forkastet/etc.), parliamentary period, enacted status, or ministry."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Free-text search in bill titles.",
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status: 'Vedtaget', 'Forkastet', 'Bortfaldet', etc.",
                    },
                    "periode_id": {
                        "type": "integer",
                        "description": "Filter by parliamentary period ID.",
                    },
                    "enacted": {
                        "type": "boolean",
                        "description": "true = only bills enacted into law, false = not enacted.",
                    },
                    "ressort": {
                        "type": "string",
                        "description": "Filter by responsible ministry.",
                    },
                    "skip": {"type": "integer", "description": "Pagination offset."},
                    "limit": {"type": "integer", "description": "Max results (default 20)."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bill_details",
            "description": (
                "Get full details about a legislative bill: metadata, text content (resume, decision, justification), "
                "and status.  The bill number format is 'L 123' or 'L-123'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "Bill number, e.g. 'L-123' or 'L 123'.",
                    },
                    "include_text": {
                        "type": "boolean",
                        "description": "If true, also fetch the text content (resume, decision text, etc.).",
                    },
                },
                "required": ["number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bill_lifecycle",
            "description": (
                "Get the full legislative process for a bill: all steps from introduction through committee "
                "to final vote, including actors at each step. Shows the progression through Fremsat → "
                "1. behandling → Udvalg → Betænkning → 2. behandling → 3. behandling → Vedtaget/Forkastet."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "Bill number, e.g. 'L-123'.",
                    },
                },
                "required": ["number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bill_actors",
            "description": (
                "Get all actors involved in a bill: sponsors (Forslagsstiller), minister, "
                "spokespeople (Ordfører), committees (Udvalg), etc."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "Bill number, e.g. 'L-123'.",
                    },
                },
                "required": ["number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_bill_documents",
            "description": (
                "Get documents related to a bill: the original bill text, committee reports (betænkning), "
                "amendments, the enacted law text, etc. Returns metadata and download URLs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "number": {
                        "type": "string",
                        "description": "Bill number, e.g. 'L-123'.",
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Filter by type: 'Lovforslag som fremsat', 'Betænkning', 'Ændringsforslag', etc.",
                    },
                },
                "required": ["number"],
            },
        },
    },
    # ------------------------------------------------------------------
    # Cases (all parliamentary case types)
    # ------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_cases",
            "description": (
                "Search all parliamentary case types (not just Lovforslag): Beslutningsforslag, "
                "Aktstykker, Forespørgsler, § 20-spørgsmål, Skriftlige spørgsmål, EU-noter, etc. "
                "Use when the query is about parliamentary cases in general, not specifically bills or laws."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Free-text search in case titles."},
                    "status": {"type": "string", "description": "Filter by status."},
                    "periode_id": {"type": "integer", "description": "Filter by parliamentary period ID."},
                    "ressort": {"type": "string", "description": "Filter by ministry."},
                    "case_type": {
                        "type": "string",
                        "description": "Filter by case type: 'Lovforslag', 'Beslutningsforslag', 'Aktstykker', etc.",
                    },
                    "skip": {"type": "integer", "description": "Pagination offset."},
                    "limit": {"type": "integer", "description": "Max results."},
                },
                "required": [],
            },
        },
    },
    # ------------------------------------------------------------------
    # Actors
    # ------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_actors",
            "description": (
                "Search parliamentary actors: politicians (Person), committees (Udvalg), "
                "ministries (Ministerium), parties (Parti), etc. "
                "Use when the user asks about a specific politician, committee, or wants to find who is involved in legislation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Search in actor name."},
                    "actor_type": {
                        "type": "string",
                        "description": "Filter by type: 'Person', 'Udvalg', 'Ministerium', 'Parti', etc.",
                    },
                    "skip": {"type": "integer", "description": "Pagination offset."},
                    "limit": {"type": "integer", "description": "Max results."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_actor_details",
            "description": (
                "Get details about a specific actor by their FT ID, including biography, "
                "party affiliation, and their committee/party memberships."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ft_id": {"type": "integer", "description": "The actor's FT ODA API ID."},
                    "include_memberships": {
                        "type": "boolean",
                        "description": "If true, also fetch party and committee memberships.",
                    },
                },
                "required": ["ft_id"],
            },
        },
    },
    # ------------------------------------------------------------------
    # Keywords
    # ------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "search_keywords",
            "description": (
                "Search topic keywords (Emneord) used to categorize parliamentary cases. "
                "Use to find keywords related to a topic, then look up cases for that keyword."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "search": {"type": "string", "description": "Search in keyword text (e.g. 'klima', 'sundhed')."},
                    "skip": {"type": "integer", "description": "Pagination offset."},
                    "limit": {"type": "integer", "description": "Max results."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cases_for_keyword",
            "description": (
                "Get all parliamentary cases tagged with a specific keyword. "
                "First use search_keywords to find the keyword FT ID, then use this."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ft_id": {"type": "integer", "description": "The keyword's FT ID."},
                    "skip": {"type": "integer", "description": "Pagination offset."},
                    "limit": {"type": "integer", "description": "Max results."},
                },
                "required": ["ft_id"],
            },
        },
    },
    # ------------------------------------------------------------------
    # Periods
    # ------------------------------------------------------------------
    {
        "type": "function",
        "function": {
            "name": "get_current_period",
            "description": (
                "Get the current parliamentary period (Folketingsår/Samling). "
                "Returns the period ID, title, start/end dates. "
                "Useful for finding out the current session or for filtering other queries."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_periods",
            "description": (
                "List parliamentary periods. Filter by type (Folketingsår, Samling) "
                "or only active periods."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "type_filter": {
                        "type": "string",
                        "description": "Filter by period type: 'Folketingsår' or 'Samling'.",
                    },
                    "active_only": {
                        "type": "boolean",
                        "description": "Only return currently active periods.",
                    },
                },
                "required": [],
            },
        },
    },
]
