# ⚖️ RetsChat

Chat interface for Danish law powered by the [Retsinformation API](https://retsinformation-api.dk) and Azure OpenAI.

Ask questions about Danish laws, bills, parliamentary cases, and actors in natural language — the LLM looks up real data from retsinformation.dk via function calling.

## Features

- **Search laws** by topic, year, ministry, or document type
- **Read law text** — full text, specific paragraphs (§), or subsections (stk.)
- **Version history** — see how a law changed over time, compare versions
- **Legislative bills** — search Lovforslag, see status, actors, process steps
- **Parliamentary cases** — all 13 case types (Beslutningsforslag, Forespørgsler, etc.)
- **Actors** — find politicians, committees, parties and their roles
- **Keywords** — explore topics and find related cases
- **Streaming** responses with live tool-call status indicators

## Setup

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Configure Azure OpenAI

Copy the example env file and fill in your Azure OpenAI credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### 3. Run

```bash
streamlit run app.py
```

## Architecture

```
User  ←→  Streamlit Chat UI  ←→  Azure OpenAI (function calling)  ←→  Retsinformation API
```

- **`app.py`** — Streamlit entrypoint with chat UI
- **`retschat/chat.py`** — Azure OpenAI orchestration with streaming + tool-calling loop
- **`retschat/tools.py`** — Function-calling tool definitions (~20 curated tools)
- **`retschat/tool_executor.py`** — Dispatches tool calls to the API client
- **`retschat/api_client.py`** — HTTP client wrapping all Retsinformation API endpoints
- **`retschat/config.py`** — Settings via pydantic-settings / `.env`

## Disclaimer

RetsChat is not legal advice. Always verify information against the official texts at [retsinformation.dk](https://www.retsinformation.dk).
