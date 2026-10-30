import json
from src.chains.rag_chain import SupportRAGChain

def run_evaluation():
    rag = SupportRAGChain()
    print("Evaluation harness loaded successfully.")

if __name__ == "__main__":
    run_evaluation()
