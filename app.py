"""RetsChat – Streamlit chat interface for Danish law."""

from __future__ import annotations

import streamlit as st

from retschat.api_client import RetsinformationClient
from retschat.chat import ChatOrchestrator
from retschat.config import get_settings
from retschat.tool_executor import ToolExecutor

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="RetsChat – Dansk lovgivning",
    page_icon="⚖️",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Helpers (defined before use)
# ---------------------------------------------------------------------------


def _tool_display_name(tool_name: str) -> str:
    """Friendly Danish name for a tool."""
    names = {
        "search_laws": "Søger i love",
        "get_law_text": "Henter lovtekst",
        "get_law_paragraph": "Henter paragraf",
        "get_law_metadata": "Henter lovdata",
        "get_law_amendments": "Henter ændringer",
        "get_law_versions": "Henter versioner",
        "compare_law_versions": "Sammenligner versioner",
        "get_legislative_history": "Henter lovhistorik",
        "get_law_actors": "Henter aktører",
        "search_bills": "Søger i lovforslag",
        "get_bill_details": "Henter lovforslag",
        "get_bill_lifecycle": "Henter lovgivningsproces",
        "get_bill_actors": "Henter aktører",
        "get_bill_documents": "Henter dokumenter",
        "search_cases": "Søger i sager",
        "search_actors": "Søger aktører",
        "get_actor_details": "Henter aktørdetaljer",
        "search_keywords": "Søger emneord",
        "get_cases_for_keyword": "Henter sager for emneord",
        "get_current_period": "Henter aktuel periode",
        "get_periods": "Henter perioder",
    }
    return names.get(tool_name, tool_name)


@st.cache_resource
def _build_orchestrator() -> ChatOrchestrator:
    settings = get_settings()
    api_client = RetsinformationClient(base_url=settings.retsinformation_base_url)
    executor = ToolExecutor(api_client, settings)
    return ChatOrchestrator(settings, executor)


def get_orchestrator() -> ChatOrchestrator:
    return _build_orchestrator()


def run_chat() -> None:
    """Execute the LLM chat loop and stream the response."""
    orchestrator = get_orchestrator()

    # Build message list for the API (only user/assistant, no tool messages)
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant", avatar="⚖️"):
        status_container = st.empty()
        content_container = st.empty()
        accumulated_content = ""

        for event in orchestrator.chat(api_messages):
            if event["type"] == "tool_call":
                tool_name = event["name"]
                status_container.status(
                    f"🔍 Kalder **{_tool_display_name(tool_name)}**...",
                    state="running",
                )

            elif event["type"] == "tool_result":
                status_container.status(
                    f"✅ **{_tool_display_name(event['name'])}** færdig",
                    state="complete",
                )

            elif event["type"] == "content_delta":
                accumulated_content += event["content"]
                content_container.markdown(accumulated_content + "▌")

            elif event["type"] == "content_done":
                accumulated_content = event["content"]
                status_container.empty()
                content_container.markdown(accumulated_content)

    if accumulated_content:
        st.session_state.messages.append(
            {"role": "assistant", "content": accumulated_content}
        )


# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚖️ RetsChat")
    st.caption(
        "Chat med dansk lovgivning via "
        "[retsinformation-api.dk](https://retsinformation-api.dk)"
    )

    st.divider()
    st.markdown("**Prøv f.eks.:**")

    examples = [
        "Søg efter love om sundhed",
        "Vis § 1 i straffeloven (lov 2024/1146)",
        "Hvilke lovforslag er vedtaget i 2025?",
        "Hvad er lejeloven?",
        "Vis ændringshistorikken for lov 2017/1002",
        "Hvem fremsatte L 83?",
    ]

    for example in examples:
        if st.button(example, key=f"ex_{example}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": example})
            st.rerun()

    st.divider()
    if st.button("🗑️ Ryd samtale", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(
        "RetsChat er ikke juridisk rådgivning. "
        "Verificér altid oplysninger mod den officielle lovtekst på retsinformation.dk."
    )

# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="⚖️"):
            st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Handle new user input
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Stil et spørgsmål om dansk lovgivning..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    run_chat()
