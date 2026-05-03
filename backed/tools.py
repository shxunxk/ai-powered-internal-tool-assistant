from rag.retriever import retriever

def search_code(query):
    """
    This tool enables to go through all the code file and 
    search for content relevant content
    """
    return retriever(query, "code")

def search_records(query):
    return retriever(query, "logs")

def search_docs(query):
    return retriever(query, "docs")