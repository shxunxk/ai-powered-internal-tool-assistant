from vectorDB import collection

def retrieve(query, intent):
    results = collection.query(
        query_texts=[query],
        n_results=5
        where={
            "type": intent
        }
    )
    return results