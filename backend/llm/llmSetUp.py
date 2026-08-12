from litellm import completion
import os

class LLM:

    def generate(self, prompt):

        response = completion(
            model="ollama/deepseek-r1:1.5b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["choices"][0]["message"]["content"]