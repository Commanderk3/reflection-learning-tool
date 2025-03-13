# Ollama API server URL
URL = "http://localhost:11434"  # Ollama's default endpoint

# Model name in Ollama
LLM_MODEL = "llama3"  # Confirmed to be available

# Embedding model for ChromaDB
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Ensure sentence-transformers is installed

# Directory for ChromaDB persistence
CHROMA_DB_DIR = "./db"  # Ensure this directory exists or will be created