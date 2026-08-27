import os
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sys
from dotenv import load_dotenv
from groq import Groq
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from mcp.server import MCPServer

load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Local Vector Store (RAG with Local Embeddings)
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vector_db = Chroma(
    collection_name="financial_rules",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Seed policy rules into vector store once
if vector_db._collection.count() == 0:
    vector_db.add_texts([
        "Standard GST rate on electronics is 18%. Tax claimed above 18% is marked suspicious.",
        "Cash purchases exceeding $200 require secondary manager approval.",
        "Unregistered vendor IDs default to high risk rating automatically."
    ])

# 2. Local MCP Server
mcp = MCPServer("FinLens-MCP")

@mcp.tool()
def calculate_allowable_deduction(invoice_amount: float, tax_rate: float) -> dict:
    deduction = invoice_amount * (tax_rate / 100.0)
    return {"eligible_deduction": deduction, "net_payable": invoice_amount - deduction}

# 3. Core Function for FastAPI Integration
def process_document(document_text: str):
    # A. Retrieve RAG Policy Context
    matched_docs = vector_db.similarity_search(document_text, k=2)
    policy_context = "\n".join([doc.page_content for doc in matched_docs])

    system_prompt = f"""You are a financial risk analyzer.
Analyze document text against these compliance rules:
{policy_context}

Return ONLY raw JSON formatted exactly as:
{{"risk_score": <number 0-100>, "audit_flags": [<string>, ...]}}"""

    # B. Call Active Groq Model (openai/gpt-oss-20b)
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": document_text}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    
    analysis_data = json.loads(response.choices[0].message.content)

    # C. Run Local MCP Deduction Tool
    mcp_result = calculate_allowable_deduction(100.00, 18.0)

    return {
        "risk_score": analysis_data.get("risk_score", 50),
        "audit_flags": analysis_data.get("audit_flags", []),
        "mcp_deduction_result": mcp_result["eligible_deduction"]
    }

# Local Test Execution
if __name__ == "__main__":
    # Check if text was passed from Node.js process via sys.argv
    if len(sys.argv) > 1:
        extracted_text = sys.argv[1]
    else:
        # Fallback test string for manual terminal testing
        extracted_text = "Invoice: Vendor #902, Total: $1500.00, Tax: $450.00 (30%), Payment: Cash."

    # Run the full RAG + Groq analysis
    ai_results = process_document(extracted_text)

    # Format the dictionary to match Supabase database expectations
    response_payload = {
        "risk_score": ai_results.get("risk_score", 0),
        "risk_level": "HIGH" if ai_results.get("risk_score", 0) > 70 else "LOW",
        "audit_flags": ai_results.get("audit_flags", []),
        "total_amount": ai_results.get("total_amount", 0.0),
        "mcp_refund": ai_results.get("mcp_refund", 0.0)
    }

    # Print raw JSON string to stdout (read by Node's stdout stream)
    print(json.dumps(response_payload))
