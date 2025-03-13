import config
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
db = Chroma(persist_directory=config.CHROMA_DB_DIR, embedding_function=embeddings)

relevance_threshold = 1.5  # Adjusted based on distance metric

def getContext(query) :

    results = db.similarity_search_with_score(query, k=5)
    relevant_docs = [(doc, score) for doc, score in results if score < relevance_threshold]
    # print("Scores:", [score for _, score in results])
    if relevant_docs:
        rag_context = " ".join(doc.page_content for doc, _ in relevant_docs)
        return rag_context
    else:
        return None

#print(getContext("Music Keyboard"))