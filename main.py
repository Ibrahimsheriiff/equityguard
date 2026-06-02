from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

if __name__ == "__main__":
    print("EquityGuard — AI Risk Assessment Agent")
    print("Type a stock ticker or question. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "q"]:
            break

        # Allow natural language or bare tickers
        if user_input.upper() == user_input and len(user_input) <= 8:
            query = f"Assess the current risk level of {user_input}"
        else:
            query = user_input

        run_agent(query, verbose=True)
        print()