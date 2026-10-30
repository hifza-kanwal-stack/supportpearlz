from langchain_openai import ChatOpenAI
from src.config import settings
from src.retrieval.retriever import SupportRetriever
from src.chains.prompts import condense_prompt, support_prompt
from src.chains.schemas import SupportResponseSchema

class SupportRAGChain:
    def __init__(self):
        self.llm = ChatOpenAI(model=settings.LLM_MODEL_NAME, temperature=settings.TEMPERATURE, openai_api_key=settings.OPENAI_API_KEY)
        self.retriever = SupportRetriever()

    def run(self, question: str, chat_history: str = "") -> SupportResponseSchema:
        standalone = question
        if chat_history.strip():
            res = (condense_prompt | self.llm).invoke({"chat_history": chat_history, "question": question})
            standalone = res.content.strip()

        docs, is_refusal = self.retriever.retrieve_with_relevance_gate(standalone)
        if is_refusal or not docs:
            return SupportResponseSchema(
                answer="I could not find this in the documentation. Please contact support@pearlzhome.example.",
                sources=[],
                confidence="none",
                answered=False
            )

        context_blocks = [f"[S{i}] source={d.metadata.get('source')}\n{d.page_content}" for i, d in enumerate(docs, 1)]
        prompt_text = support_prompt.format(context="\n\n".join(context_blocks), question=standalone)
        structured_llm = self.llm.with_structured_output(SupportResponseSchema)
        result = structured_llm.invoke(prompt_text)

        # Don't trust the model to cite sources: use the files actually retrieved.
        if result.answered:
            result.sources = list(dict.fromkeys(str(d.metadata.get("source")) for d in docs))
        else:
            result.sources = []
        return result
