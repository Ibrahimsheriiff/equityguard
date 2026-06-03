import os
try:
    import streamlit as st
    ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

MODEL = "claude-sonnet-4-6"
MAX_ITERATIONS = 6
MAX_TOKENS = 2000