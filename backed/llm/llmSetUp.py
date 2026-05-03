import json
import inspect
from litellm import completion

class LLM:

    def generate(self, prompt):

        response = completion(
            model="deepseek/deepseek-chat",
            api_key="YOUR_API_KEY",
            api_base="https://api.deepseek.com",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["choices"][0]["message"]["content"]