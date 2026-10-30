import os
import sys
from pathlib import Path

# Make `src.*` imports work when launched via `streamlit run src/app_streamlit.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from langchain_openai import OpenAIEmbeddings
from src.config import settings
from src.chains.rag_chain import SupportRAGChain
from src.chains.memory import ConversationMemory
from src.ingestion.build_index import build_kb_index

st.set_page_config(page_title="SupportPearlz | AI Support", page_icon="🦪", layout="wide")

# ---------- session state ----------
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("memory", ConversationMemory())
st.session_state.setdefault("rag_chain", None)


def verify_key(key: str) -> str | None:
    """Return None if the key works, otherwise a short error message."""
    try:
        OpenAIEmbeddings(model=settings.EMBEDDING_MODEL_NAME, openai_api_key=key).embed_query("ping")
        return None
    except Exception as e:
        msg = str(e)
        if "401" in msg or "invalid_api_key" in msg or "Incorrect API key" in msg:
            return "Invalid API key. Please check it and try again."
        if "429" in msg or "insufficient_quota" in msg:
            return "This key has no remaining quota/billing. Check your OpenAI account."
        return f"Could not verify the key: {msg[:200]}"


def logout():
    os.environ.pop("OPENAI_API_KEY", None)
    settings.OPENAI_API_KEY = ""
    st.session_state.authenticated = False
    st.session_state.rag_chain = None
    st.session_state.memory.reset()


# ---------- login screen ----------
if not st.session_state.authenticated:
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        st.markdown("<h1 style='text-align:center'>🦪 SupportPearlz</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center'>Sign in with your OpenAI API key to open the console.</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            key_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
            submitted = st.form_submit_button("Sign in", use_container_width=True)
        if submitted:
            key = key_input.strip()
            if not key:
                st.error("Please enter your API key.")
            else:
                with st.spinner("Verifying key..."):
                    error = verify_key(key)
                if error:
                    st.error(error)
                else:
                    os.environ["OPENAI_API_KEY"] = key
                    settings.OPENAI_API_KEY = key
                    st.session_state.authenticated = True
                    st.rerun()
    st.stop()

# ---------- console (only reached after login) ----------
with st.sidebar:
    st.markdown("# 🦪")
    st.title("SupportPearlz Console")
    st.caption("🔒 Signed in")

    if st.button("Rebuild Index"):
        with st.spinner("Rebuilding index..."):
            build_kb_index(force_rebuild=True)
        st.session_state.rag_chain = None  # reload the fresh index
        st.success("Index rebuilt!")
    if st.button("Reset Chat"):
        st.session_state.memory.reset()
        st.rerun()
    if st.button("Sign out"):
        logout()
        st.rerun()

st.title("🦪 SupportPearlz Knowledge Agent")
st.markdown("Customer Support RAG Assistant (AAI-407/PRAC-03)")


def get_chain():
    """Create the chain; build the index automatically on first run."""
    try:
        return SupportRAGChain()
    except RuntimeError:
        with st.spinner("Building knowledge base index (first run)..."):
            build_kb_index(force_rebuild=True)
        return SupportRAGChain()


if st.session_state.rag_chain is None:
    try:
        st.session_state.rag_chain = get_chain()
    except Exception as e:
        st.error(f"Could not start the agent: {e}")
        st.stop()

for role, text in st.session_state.memory.history:
    with st.chat_message(role):
        st.markdown(text)

if prompt := st.chat_input("Ask a support question..."):
    history_text = st.session_state.memory.get_formatted_history()  # before adding this turn
    st.session_state.memory.add_turn("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.rag_chain.run(prompt, history_text)
            st.markdown(response.answer)
            if response.sources:
                st.info(f"Sources: {', '.join(response.sources)} | Confidence: {response.confidence.upper()}")
            st.session_state.memory.add_turn("assistant", response.answer)
