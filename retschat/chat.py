"""Azure OpenAI chat orchestration with function-calling loop."""

from __future__ import annotations

import json
import logging
from typing import Any, Generator

from openai import AzureOpenAI
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
)

from retschat.config import Settings
from retschat.tool_executor import ToolExecutor
from retschat.tools import TOOLS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Du er **RetsChat**, en AI-assistent der hjælper med dansk lovgivning ved hjælp af data fra retsinformation.dk.

## Regler
- Svar altid på det sprog brugeren skriver (dansk eller engelsk).
- Brug ALTID dine værktøjer til at slå information op — stol ikke på din træningsdata for lovtekster.
- Citér altid specifikke lovhenvisninger (år/nummer, §, stk.) når du henviser til lovtekst.
- Når du viser lovtekst, formatér den tydeligt med markdown.
- Hvis en søgning ikke giver resultater, foreslå alternative søgeord eller filtre.
- Du kan kæde flere tool-kald sammen for at besvare komplekse spørgsmål.
- Forklar juridiske begreber i letforståeligt sprog, men gør det klart at du ikke er juridisk rådgiver.
- Dagens dato er {date}.

## Eksempler på hvad du kan hjælpe med
- Søge i love og bekendtgørelser
- Vise specifikke paragraffer
- Finde ændringshistorik for en lov
- Se hvem der fremsatte et lovforslag
- Finde lovforslag om et bestemt emne
- Sammenligne versioner af en lov
- Vise den lovgivningsmæssige proces
"""


class ChatOrchestrator:
    """Manages the conversation loop with Azure OpenAI and tool execution."""

    def __init__(self, settings: Settings, tool_executor: ToolExecutor) -> None:
        self.settings = settings
        self.tool_executor = tool_executor
        self.openai_client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        self.deployment = settings.azure_openai_deployment

    def get_system_message(self) -> dict[str, str]:
        from datetime import date

        return {
            "role": "system",
            "content": SYSTEM_PROMPT.format(date=date.today().isoformat()),
        }

    def chat(
        self,
        messages: list[dict[str, Any]],
    ) -> Generator[dict[str, Any], None, None]:
        """Run a chat turn, yielding events for the UI.

        Yields dicts with keys:
          - {"type": "tool_call", "name": str, "arguments": dict}
          - {"type": "tool_result", "name": str, "content": str}
          - {"type": "content_delta", "content": str}
          - {"type": "content_done", "content": str}
        """
        full_messages: list[Any] = [self.get_system_message()] + messages
        rounds = 0

        while rounds < self.settings.max_tool_rounds:
            rounds += 1

            response = self.openai_client.chat.completions.create(
                model=self.deployment,
                messages=full_messages,
                tools=TOOLS,  # type: ignore[arg-type]
                tool_choice="auto",
                max_completion_tokens=self.settings.max_tokens,
                stream=True,
            )

            # Accumulate the streamed response
            collected_content = ""
            tool_calls_map: dict[int, dict[str, str]] = {}
            finish_reason = None

            for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                finish_reason = chunk.choices[0].finish_reason

                # Content streaming
                if delta.content:
                    collected_content += delta.content
                    yield {"type": "content_delta", "content": delta.content}

                # Tool call accumulation
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_map:
                            tool_calls_map[idx] = {
                                "id": "",
                                "name": "",
                                "arguments": "",
                            }
                        if tc.id:
                            tool_calls_map[idx]["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                tool_calls_map[idx]["name"] = tc.function.name
                            if tc.function.arguments:
                                tool_calls_map[idx]["arguments"] += (
                                    tc.function.arguments
                                )

            # If we got content and no tool calls, we're done
            if finish_reason != "tool_calls" and not tool_calls_map:
                yield {"type": "content_done", "content": collected_content}
                return

            # If there were tool calls, execute them
            if tool_calls_map:
                # Build the assistant message with tool calls
                assistant_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": collected_content or None,
                    "tool_calls": [],
                }
                for idx in sorted(tool_calls_map.keys()):
                    tc_data = tool_calls_map[idx]
                    assistant_msg["tool_calls"].append({
                        "id": tc_data["id"],
                        "type": "function",
                        "function": {
                            "name": tc_data["name"],
                            "arguments": tc_data["arguments"],
                        },
                    })
                full_messages.append(assistant_msg)

                # Execute each tool call
                for idx in sorted(tool_calls_map.keys()):
                    tc_data = tool_calls_map[idx]
                    tool_name = tc_data["name"]
                    try:
                        arguments = json.loads(tc_data["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}

                    yield {
                        "type": "tool_call",
                        "name": tool_name,
                        "arguments": arguments,
                    }

                    result = self.tool_executor.execute(tool_name, arguments)

                    yield {
                        "type": "tool_result",
                        "name": tool_name,
                        "content": result[:200] + "..." if len(result) > 200 else result,
                    }

                    full_messages.append({
                        "role": "tool",
                        "tool_call_id": tc_data["id"],
                        "content": result,
                    })

                # Loop back to let the LLM process the tool results
                continue

            # Fallback: if we got here somehow, yield what we have
            yield {"type": "content_done", "content": collected_content}
            return

        # Max rounds reached
        yield {
            "type": "content_done",
            "content": "Jeg har nået det maksimale antal værktøjskald. Prøv at stille et mere specifikt spørgsmål.",
        }
