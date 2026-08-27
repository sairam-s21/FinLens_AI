from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings

# Local CPU-based free embeddings (No API calls required)
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# Local vector store stored in your /ai directory
vector_db = Chroma(
    collection_name="tax_policies",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

def query_policies(document_text: str):
    # Returns matching tax rules locally
    results = vector_db.similarity_search(document_text, k=2)
    return [doc.page_content for doc in results]