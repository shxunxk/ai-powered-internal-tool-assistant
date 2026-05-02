def ragPipeline(query, context, client):

    context = "\n".join(context)

    prompt = f"""
    You are an enterprise AI operations assistant.

    Question:
    {query}


    Retrieved Context:
    {context}

    Answer using ONLY the provided context.
    """
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content    