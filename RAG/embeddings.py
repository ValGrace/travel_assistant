from text_chunks import TextChunks
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings


class SentenceTransformerEmbeddings(Embeddings):
    """Adapter so SentenceTransformer satisfies LangChain's Embeddings interface."""

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text):
        return self.model.encode(text, convert_to_numpy=True).tolist()


class ContextEmbed:
    def __init__(self, files):
        self.files = files
        self.embedding_fn = SentenceTransformerEmbeddings('bert-base-nli-mean-tokens')

    def load_chunks(self):
        chunky = TextChunks(self.files)
        self.chunks = chunky.load_and_chunk_data()
        return self.chunks

    def create_vectorstore(self):
        vector_store = Chroma.from_texts(
            texts=self.chunks,
            embedding=self.embedding_fn,          # <-- an Embeddings object, not a numpy array
            collection_name="kenyan-tourism-collection",
            persist_directory="data/chroma_db",
        )
        vector_store.persist()
        return vector_store


if __name__ == "__main__":
    files = [
        "data/gold_data/parks.txt",
        "data/gold_data/nairobi_hotels.txt",
        "data/gold_data/magical_kenya.txt",
        "data/gold_data/kenyan_hotels.txt",
        "data/gold_data/kenyan_campsites.txt",
        "data/gold_data/kws_prices.txt",
    ]
    embeds = ContextEmbed(files)
    embeds.load_chunks()
    stored_vectors = embeds.create_vectorstore()
    stored_vectors