from text_chunks import TextChunks
from sentence_transformers import SentenceTransformer

class ContextEmbed:
    def __init__(self, files):
        self.files = files
        self.model = SentenceTransformer('bert-base-nli-mean-tokens')


    def generate_embedding(self):
        # model = SentenceTransformer('bert-base-nli-mean-tokens')

        chunky = TextChunks(self.files)
        chunks = chunky.load_and_chunk_data()

        embeddings = self.model.encode(chunks)
        similarities = self.model.similarity(embeddings, embeddings)
        print(similarities)
        return embeddings

if __name__ == "__main__":
    files = [
                    "data/gold_data/parks.txt",
                    "data/gold_data/nairobi_hotels.txt",
                    "data/gold_data/magical_kenya.txt",
                    "data/gold_data/kenyan_hotels.txt",
                    "data/gold_data/kenyan_campsites.txt",
                    "data/gold_data/kws_prices.txt"
                ]
    embeds = ContextEmbed(files)
    newembed = embeds.generate_embedding()
    print(f"Embedding dhape: {newembed.shape}")