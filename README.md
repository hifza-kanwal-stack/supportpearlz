# SupportPearlz: RAG Customer Support Knowledge Agent (AAI-407/PRAC-03)

SupportPearlz is a production-grade Retrieval-Augmented Generation (RAG) customer support knowledge agent built with Python, LangChain, and Streamlit.

## Quickstart
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`.
3. Build index: `python -m src.ingestion.build_index`
4. Run UI: `streamlit run src/app_streamlit.py`
