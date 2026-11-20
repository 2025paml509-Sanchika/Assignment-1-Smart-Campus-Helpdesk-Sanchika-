"""Local Ollama LLM agent with actual LangChain tool calling.

Requires Ollama running locally and a tool-capable model, e.g. qwen3.
The agent executes tool calls returned by the model and sends tool results
back to the model before requesting its final recommendation.
"""
import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools.helpdesk_tools import ALL_TOOLS


class LLMAgent:
    def __init__(self, model="qwen3:latest", base_url="http://localhost:11434"):
        self.model_name = model
        self.llm = ChatOllama(model=model, base_url=base_url, temperature=0)
        self.tools = {tool.name: tool for tool in ALL_TOOLS}
        self.tool_enabled_llm = self.llm.bind_tools(ALL_TOOLS)

    def decide(self, ticket: dict) -> dict:
        system = SystemMessage(content=(
            "You are a campus IT helpdesk triage assistant. You must use tools before deciding. "
            "Call get_ticket_details and search_known_fixes at minimum. Also call check_service_status "
            "for network/service incidents and get_support_policy before finalizing. "
            "Use only returned tool evidence; distinguish suspected from confirmed outages. "
            "Return concise JSON with priority (P1 - Critical/P2 - High/P3 - Normal/P4 - Low), "
            "action, evidence, uncertainty, and reasoning. Never claim to have changed a real system."
        ))
        human = HumanMessage(content=(
            "Analyze this shared simulated ticket. ticket_id="
            + ticket["ticket_id"] + "\nTicket data:\n" + json.dumps(ticket, ensure_ascii=False)
        ))
        messages = [system, human]
        evidence = []
        tool_names_called = []
        max_rounds = 6

        for _ in range(max_rounds):
            response = self.tool_enabled_llm.invoke(messages)
            messages.append(response)
            calls = getattr(response, "tool_calls", []) or []
            if not calls:
                final_text = response.content if isinstance(response.content, str) else str(response.content)
                if len(tool_names_called) < 2:
                    raise RuntimeError(
                        "The Ollama model did not call at least two tools. "
                        "Check that the selected model supports tool calling (for example, qwen3)."
                    )
                return {
                    "agent": "Ollama LLM",
                    "priority": self._extract_priority(final_text),
                    "action": "See LLM recommendation",
                    "reasoning": final_text,
                    "tool_calls": tool_names_called,
                    "evidence": evidence,
                    "model": self.model_name,
                }

            for call in calls:
                name = call.get("name")
                args = call.get("args", {})
                if name not in self.tools:
                    tool_result = f"Tool '{name}' is not available."
                else:
                    tool_names_called.append(name)
                    try:
                        tool_result = self.tools[name].invoke(args)
                    except Exception as exc:
                        tool_result = f"Tool execution error: {exc}"
                evidence.append({"tool": name, "arguments": args, "result": str(tool_result)})
                messages.append(ToolMessage(
                    content=str(tool_result),
                    tool_call_id=call.get("id", name or "unknown"),
                ))

        raise RuntimeError("LLM exceeded the tool-call limit without producing a final answer.")

    @staticmethod
    def _extract_priority(text: str) -> str:
        upper = text.upper()
        for priority in ("P1 - CRITICAL", "P2 - HIGH", "P3 - NORMAL", "P4 - LOW"):
            if priority in upper:
                return priority.title().replace("P1 - Critical", "P1 - Critical") \
                    .replace("P2 - High", "P2 - High") \
                    .replace("P3 - Normal", "P3 - Normal") \
                    .replace("P4 - Low", "P4 - Low")
        return "Needs review"
