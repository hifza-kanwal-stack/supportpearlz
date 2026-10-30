import os
import glob
import pandas as pd
from typing import List
from langchain_core.documents import Document
from src.utils.logging_setup import logger

class DocumentLoaderService:
    def __init__(self, kb_dir: str = "data/knowledge_base"):
        self.kb_dir = kb_dir

    def load_documents(self) -> List[Document]:
        documents = []
        if not os.path.exists(self.kb_dir):
            return documents
        files = glob.glob(os.path.join(self.kb_dir, "**/*.*"), recursive=True)
        for filepath in files:
            ext = os.path.splitext(filepath)[1].lower()
            filename = os.path.basename(filepath)
            try:
                if ext in [".md", ".txt"]:
                    with open(filepath, "r", encoding="utf-8") as f:
                        text = f.read()
                    documents.append(Document(page_content=text, metadata={"source": filename, "doc_type": "policy", "location": "section"}))
                elif ext == ".csv":
                    df = pd.read_csv(filepath)
                    for idx, row in df.iterrows():
                        row_text = ", ".join([f"{col}: {val}" for col, val in row.items()])
                        documents.append(Document(page_content=row_text, metadata={"source": filename, "doc_type": "pricing", "location": f"row-{idx+1}"}))
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
        return documents
