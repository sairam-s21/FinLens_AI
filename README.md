# FinLens_AI
This project is our practice for an upcoming hackathon. 
**Project Architecture:**
## System Architecture

The following diagram illustrates the complete end-to-end data flow of **FinLens AI**, from client authentication to automated AI risk scoring and agentic execution:

+-----------------------------------------------------------------------------------+
|                                  REACT DASHBOARD                                  |
|  - File Dropzone / Document Input      - Live Risk Score & Audit Visualizer       |
|  - Supabase Auth Handler               - History & Past Reports View              |
+-----------------------------------------+-----------------------------------------+
                                          |
                        HTTP POST /api/v1/analyze
                        Header: Authorization: Bearer <SUPABASE_JWT>
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                 FASTAPI BACKEND                                   |
|  - JWT Middleware Token Validation      - Endpoint Routing & Parsing              |
|  - Supabase DB Client Integration      - Error Handling & Payload Structuring     |
+-------------------+-----------------------------------+---------------------------+
                    |                                   |
        Write Records / Fetch Logs                 Invoke AI Pipeline
                    |                                   |
                    v                                   v
+-----------------------+           +-----------------------------------------------+
|     SUPABASE DB       |           |                AI & AGENT WORKFLOW            |
| - Users & Auth Tokens |           | 1. Fine-Tuned LLM (llama-3.1-8b-instant)      |
| - Invoices & Logs     |           |    -> Evaluates Document Risk Score & Flags   |
+-----------------------+           | 2. RAG Engine (LangChain + ChromaDB)          |
                                    |    -> Queries Tax Policy Vector Store         |
                                    | 3. MCP Server (Anthropic SDK)                 |
                                    |    -> Executes Tax Refund & Calculation Tools |
                                    +-----------------------------------------------+
