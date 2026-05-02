from litellm import completion

class RouterLLM:
    def generate(self, query, context):

        prompt = f"""
        {role}

        Context:
        {context}

        Question:
        {query}
        """

        response = completion(
            model="deepseek/deepseek-chat",
            api_key="YOUR_KEY",
            api_base="https://api.deepseek.com",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response["choices"][0]["message"]["content"]