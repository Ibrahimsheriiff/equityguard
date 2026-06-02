import anthropic
import json
from tools import TOOL_SCHEMAS, execute_tool
from prompts import SYSTEM_PROMPT
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 6  # safety cap — prevents runaway loops and cost blowout


def run_agent(query: str, verbose: bool = True) -> str:
    """
    The ReAct agent loop.

    This is the core of the project. It:
    1. Sends the query + all tool schemas to Claude
    2. Claude responds with either a tool call (Act) or a final answer
    3. If tool call → we execute it, feed result back (Observe), loop again
    4. If final answer → we return it

    Nothing here is hardcoded logic. Claude decides what to investigate.
    """

    messages = [{"role": "user", "content": query}]
    iteration = 0

    if verbose:
        print(f"\n{'='*60}")
        print(f"EQUITYGUARD AGENT STARTING")
        print(f"Query: {query}")
        print(f"{'='*60}\n")

    while iteration < MAX_ITERATIONS:
        iteration += 1

        if verbose:
            print(f"--- Iteration {iteration} ---")

        # ── THINK + ACT: send to Claude ────────────────────────────────────
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if verbose:
            print(f"Stop reason: {response.stop_reason}")

        # ── CHECK: did Claude finish, or does it want to call a tool? ───────
        if response.stop_reason == "end_turn":
            # Claude is done — extract the final text answer
            final_answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    final_answer += block.text

            if verbose:
                print(f"\n{'='*60}")
                print("FINAL ANSWER:")
                print(f"{'='*60}")
                print(final_answer)

            return final_answer

        elif response.stop_reason == "tool_use":
            # Claude wants to call one or more tools
            # Add Claude's response to message history first
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call Claude requested
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    if verbose:
                        print(f"Tool call: {tool_name}({json.dumps(tool_input)})")

                    # ── OBSERVE: execute the tool ───────────────────────────
                    result = execute_tool(tool_name, tool_input)

                    if verbose:
                        # Pretty print a preview of the result
                        try:
                            parsed = json.loads(result)
                            preview = json.dumps(parsed, indent=2)[:400]
                            print(f"Result preview:\n{preview}\n")
                        except Exception:
                            print(f"Result: {result[:200]}\n")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # Feed all tool results back to Claude for next Think step
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason
            if verbose:
                print(f"Unexpected stop reason: {response.stop_reason}")
            break

    return "Agent reached maximum iterations without a final answer."