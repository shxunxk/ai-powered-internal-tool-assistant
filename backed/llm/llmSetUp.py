from litellm import completion
import os

class LLM:
    def generate(self, query prompt):

        response = completion(
            model="deepseek/deepseek-chat",
            api_key="YOUR_KEY",
            api_base="https://api.deepseek.com",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response["choices"][0]["message"]["content"]