from openai.types.responses.response_reasoning_item import Summary
from agents.retrievalAgent import RetrievalAgent
from rag.retriever import retriever
from rag.llm.llmSetUp import RouterLLM, SummaryLLM
from tools import search_code, search_docs, search_records

CLASSIFIER_PROMPT = """
            You are a query classification system for an internal AI assistant.

            Your job is to analyze the user query and extract:

            1. task → high-level intent category
            2. subtask → more specific intent within the task
            3. language → language of the query (ISO code)

            ---

            ## TASK DEFINITIONS:

            Choose exactly ONE:

            - code → queries related to programming, debugging, APIs, errors, code logic, development, stack traces
            - documentation → queries related to system design, architecture, project explanation, tech stack, setup guides, 
            queries related to production issues, outages, latency, logs, metrics, monitoring, failures, queries related
            to rules, security, compliance, access control, HR

            ---

            ## TASK DETAILS:

            If task = code:
            - bug_fix → fixing errors, exceptions, stack traces
            - api_usage → how to use APIs or endpoints
            - architecture → system design, structure, design patterns
            - config → environment setup, configs, deployment settings
            - general → anything else

            If task = documentation:
            - tech_stack → technologies used, project overview, architecture explanation
            - setup → installation, setup steps, onboarding
            - explanation → conceptual explanation of system or module
            - reference → definitions, documentation lookup
            - latency → slow performance, delays
            - outage → system down, service unavailable
            - error_spike → sudden increase in errors
            - logs → log analysis
            - metrics → monitoring, dashboards, KPIs
            - general → anything else
            - security → security rules, authentication, authorization
            - compliance → regulations, audits, governance
            - hr → HR policies
            - access_control → permissions, roles

            ---

            ## OUTPUT FORMAT (STRICT JSON ONLY):

            {
            "task": "...",
            }

            ---

            ## RULES:
            - Output ONLY valid JSON
            - Do NOT explain anything
            - Do NOT add extra text
            - Be conservative (if unsure, choose "documentation" or "general")
            - Focus on intent, not keywords

            ---

            ## EXAMPLES:

            Query: "Why is my API returning 500 error?"
            Output:
            {
            "task": "code",
            }

            ---

            Query: "what tech stack is used in this project and how does it scale?"
            Output:
            {
            "task": "documentation",
            }

            ---

            Query: "latency spike in production logs today"
            Output:
            {
            "task": "incident",
            }

            ---

            Query: "reset password kaise hota hai"
            Output:
            {
            "task": "documentation",
            }

            ---

            Now classify this query:

            {query}
            """

CLASSIFIER_PROMPT = """
            You are a query classification system for an internal AI assistant.

            Your job is to analyze the user query and extract:

            1. task → high-level intent category
            2. subtask → more specific intent within the task
            3. language → language of the query (ISO code)

            ---

            ## TASK DEFINITIONS:

            Choose exactly ONE:

            - code → queries related to programming, debugging, APIs, errors, code logic, development, stack traces
            - documentation → queries related to system design, architecture, project explanation, tech stack, setup guides, 
            queries related to production issues, outages, latency, logs, metrics, monitoring, failures, queries related
            to rules, security, compliance, access control, HR

            ---

            ## TASK DETAILS:

            If task = code:
            - bug_fix → fixing errors, exceptions, stack traces
            - api_usage → how to use APIs or endpoints
            - architecture → system design, structure, design patterns
            - config → environment setup, configs, deployment settings
            - general → anything else

            If task = documentation:
            - tech_stack → technologies used, project overview, architecture explanation
            - setup → installation, setup steps, onboarding
            - explanation → conceptual explanation of system or module
            - reference → definitions, documentation lookup
            - latency → slow performance, delays
            - outage → system down, service unavailable
            - error_spike → sudden increase in errors
            - logs → log analysis
            - metrics → monitoring, dashboards, KPIs
            - general → anything else
            - security → security rules, authentication, authorization
            - compliance → regulations, audits, governance
            - hr → HR policies
            - access_control → permissions, roles

            ---

            ## OUTPUT FORMAT (STRICT JSON ONLY):

            {
            "task": "...",
            }

            ---

            ## RULES:
            - Output ONLY valid JSON
            - Do NOT explain anything
            - Do NOT add extra text
            - Be conservative (if unsure, choose "documentation" or "general")
            - Focus on intent, not keywords

            ---

            ## EXAMPLES:

            Query: "Why is my API returning 500 error?"
            Output:
            {
            "task": "code",
            }

            ---

            Query: "what tech stack is used in this project and how does it scale?"
            Output:
            {
            "task": "documentation",
            }

            ---

            Query: "latency spike in production logs today"
            Output:
            {
            "task": "incident",
            }

            ---

            Query: "reset password kaise hota hai"
            Output:
            {
            "task": "documentation",
            }

            ---

            Now classify this query:

            {query}
            """

SUMMARY_PROMPT = """
                You are an internal AI assistant responsible for answering user questions using retrieved context.

                You are the FINAL step in a retrieval-augmented generation pipeline.

                ---

                ## YOUR JOB:
                - Use ONLY the provided context
                - Combine relevant information into a clear, coherent answer
                - Do NOT retrieve or assume any external knowledge
                - If context is insufficient, explicitly say so

                ---

                ## RULES:
                - Do NOT hallucinate or guess missing details
                - Do NOT mention "based on context" in the final answer
                - Be concise but complete
                - Prefer structured answers when useful (bullet points or steps)
                - If there are multiple interpretations, mention them briefly

                ---

                ## OUTPUT STYLE:
                - Direct answer first
                - Then supporting explanation if needed
                - Keep it user-friendly and technical when required

                ---

                ## CONTEXT:
                {context}

                ---

                ## QUESTION:
                {query}

                ---

                Now generate the final answer:
                """


                
user_query = "Where is JWT validation implemented?"

retrievedResult = RetrievalAgent(RouterLLM, SummaryLLM, tools = [search_records, search_code, search_docs]).run(user_query)

print(retrievedResult)