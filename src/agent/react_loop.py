import re
import json
import anthropic
from src.utils.config import ANTHROPIC_API_KEY, MODEL, MAX_ITERATIONS, MAX_TOKENS
from src.agent.prompts import SYSTEM_PROMPT
from src.agent.tool_registry import TOOL_SCHEMAS, execute_tool
from src.agent.trace import AgentTrace

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TOOL_SUMMARIES = {
    "get_price_data":           lambda r: f"Price ${r.get('current_price','?')}, beta {r.get('beta','?')}, 30d vol {r.get('volatility_30d_annualised_pct','?')}%",
    "get_technical_signals":    lambda r: f"RSI {r.get('rsi_14','?')} ({r.get('rsi_signal','?')}), MACD {r.get('macd_signal','?')}, Bollinger {r.get('bollinger_signal','?')}",
    "get_news_sentiment":       lambda r: f"Found {r.get('headline_count', 0)} headlines",
    "get_earnings_risk":        lambda r: f"Earnings risk: {r.get('earnings_risk','unknown')}",
    "retrieve_company_docs":    lambda r: f"Found {r.get('docs_found', 0)} internal document(s) for {r.get('ticker','?')}",
    "search_company_knowledge": lambda r: f"Vector search returned {r.get('chunks_found', 0)} relevant chunks",
}

def summarise_result(tool_name: str, result_json: str) -> str:
    """Turn raw tool JSON into a one-line human-readable summary for the trace."""
    try:
        r = json.loads(result_json)
        if "error" in r:
            return f"Error: {r['error']}"
        fn = TOOL_SUMMARIES.get(tool_name)
        return fn(r) if fn else result_json[:120]
    except Exception:
        return result_json[:120]

def extract_thought(response_content) -> str:
    """Pull the THOUGHT text out of Claude's response before a tool call."""
    for block in response_content:
        if hasattr(block, "text") and "THOUGHT:" in block.text:
            match = re.search(r"THOUGHT:\s*(.+?)(?:\n|ACTION:|$)", block.text, re.DOTALL)
            if match:
                return match.group(1).strip()[:200]
    return "Deciding next step..."


def run_agent(query: str, ticker: str = "", verbose: bool = True):
    """
    The ReAct agent loop.
    Returns: (final_answer, trace)
    """
    messages = [{"role": "user", "content": query}]
    trace = AgentTrace(ticker=ticker or query, query=query)

    if verbose:
        print(f"\n{'='*60}\nEQUITYGUARD AGENT\nQuery: {query}\n{'='*60}\n")

    for iteration in range(1, MAX_ITERATIONS + 1):
        if verbose:
            print(f"--- Iteration {iteration} ---")

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        # ── Agent is done ──────────────────────────────────────────────────
        if response.stop_reason == "end_turn":
            final_answer = "".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            score_match = re.search(r'(\d+)/10', final_answer)
            risk_score = int(score_match.group(1)) if score_match else None
            trace.complete(final_answer, risk_score)
            trace.save()

            if verbose:
                print(f"\nFINAL ANSWER:\n{final_answer}")

            return final_answer, trace

        # ── Agent wants to call a tool ─────────────────────────────────────
        elif response.stop_reason == "tool_use":
            thought = extract_thought(response.content)
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name  = block.name
                    tool_input = block.input

                    if verbose:
                        print(f"Thought: {thought}")
                        print(f"Tool: {tool_name}({tool_input})")

                    result  = execute_tool(tool_name, tool_input)
                    summary = summarise_result(tool_name, result)

                    trace.add_step(
                        thought=thought,
                        tool_name=tool_name,
                        tool_input=tool_input,
                        tool_output_summary=summary,
                    )

                    if verbose:
                        print(f"Result: {summary}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})

        else:
            break

    return "Agent reached maximum iterations.", trace