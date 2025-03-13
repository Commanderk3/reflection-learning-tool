import os
import config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)

def load_markdown_files(directory):
    documents = []
    for file in os.listdir(directory):
        if file.endswith(".md"):
            with open(os.path.join(directory, file), "r", encoding="utf-8") as f:
                content = f.read()
                documents.append(Document(page_content=content))
    return documents

docs = load_markdown_files("data")

# Split Markdown files into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = text_splitter.split_documents(docs)

db = Chroma.from_documents(split_docs, embeddings, persist_directory=config.CHROMA_DB_DIR)

print("✅ Markdown documents embedded and stored in ChromaDB.")