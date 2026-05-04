from litellm import completion
import os

class LLM:

    def generate(self, prompt):

        response = completion(
            model="ollama/deepseek-r1:1.5b",
            # api_key= os.getenv("DEEPSEEK_API_KEY"),
            # api_base= os.getenv("DEEPSEEK_BASE_URL"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["choices"][0]["message"]["content"]