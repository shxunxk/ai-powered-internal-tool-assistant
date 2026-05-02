class RetrievalAgent:
    def __init__(self, retriever, RouterLLM, SummaryLLM):
        self.retriever = retriever
        self.llm1 = RouterLLM
        self.llm2 = SummaryLLM

    def build_context(self, docs):
        return "\n\n".join(docs)

    def run(self, query):

        #setp 0: find catgeories
        result = self.llm.generate(query)

        # STEP 1: retrieve
        docs = self.retriever(query, k=20)

        # STEP 3: build context
        context = self.build_context(docs)

        # STEP 4: LLM generation
        return self.llm.generate(query, context)