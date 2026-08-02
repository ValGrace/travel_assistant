from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import Chroma
from embeddings import SentenceTransformerEmbeddings

class RetrieveContext:
    def __init__(self, vector_store, reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.vector_store = vector_store
        self.reranker = CrossEncoder(reranker_model)

    def retrieve(self, query, top_n_vector=25, top_k_final=5):
        # stahe 1: vector search ~ wide candidate pool
        candidates = self.vector_store.similarity_search(query, k=top_n_vector)

        pairs = [(query, doc.page_content) for doc in candidates]
        scores = self.reranker.predict(pairs)

        reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

        return [doc for doc, score in reranked[:top_k_final]]

embedding_fn = SentenceTransformerEmbeddings('bert-base-nli-mean-tokens')
vector_store = Chroma(
collection_name="kenyan-tourism-collection",
embedding_function=embedding_fn,
persist_directory="data/chroma_db"
)

retriever = RetrieveContext(vector_store=vector_store)
results = retriever.retrieve("best accommodations near Maasai mara", top_n_vector=25, top_k_final=5)

for doc in results:
    print(doc.page_content)
    print("---")