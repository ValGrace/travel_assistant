from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import Chroma
from embeddings import SentenceTransformerEmbeddings
import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()
class RetrieveContext:
    def __init__(self, vector_store, reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.vector_store = vector_store
        self.reranker = CrossEncoder(reranker_model)
        self.client = None
        self.model_name = "gemini-3.5-flash"

    def retrieve(self, query, top_n_vector=25, top_k_final=5):
        # stahe 1: vector search ~ wide candidate pool
        candidates = self.vector_store.similarity_search(query, k=top_n_vector)
        if not candidates:
            return[]
        pairs = [(query, doc.page_content) for doc in candidates]
        scores = self.reranker.predict(pairs)

        reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

        return [doc for doc, score in reranked[:top_k_final]]
    
    def setup_model(self):
        """---Setup Gemini Model---"""
        print("Initializing Gemini model...")
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        self.client = genai.Client(api_key=api_key)
        # self.model = client.GenerativeModel('gemini-3.5-flash')
        print("Client initialized successfully")

    def query_response(self, tourism_query):
        if not self.client:
            raise ValueError("Client not initialized. Run setup_model() first.")

        relevant_chunks = self.retrieve(tourism_query, top_n_vector=25, top_k_final=5)
        context = "\n\n".join(doc.page_content for doc in relevant_chunks)

        prompt_template =f""" 
        You are a travel assistant knowlegeable about hotels, destinations, safari trips, coastal vacations, and travel planning in Kenya. If the answer is not in the context, say you don't have enough information - do not guess
         
        Context: {context}

        Lets plan your next trip: {tourism_query}

        Instructions:
        1. Search for relevant hotels, destinations, prices, amenities, locations, safari trips in the context
        2. Provide the most suitable recommendations.
        3. Explain why the recommendation briefly.
        4. Ask the user follow up questions to generate the most accurate answer.
        5. Rewrite the returned context into plain english and natural language conversion.
        6. For each returned context, generate a day by day itenary plan with where the accomodations and activities and include the cost. Plans balance nearby must-see highlights with hidden gems.
          
         """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_template
            )
        return response.text



if __name__ == "__main__":
    embedding_fn = SentenceTransformerEmbeddings('all-mpnet-base-v2')
    vector_store = Chroma(
    collection_name="kenyan-tourism-collection",
    embedding_function=embedding_fn,
    persist_directory="data/chroma_db"
    )

    retriever = RetrieveContext(vector_store=vector_store)
    # results = retriever.retrieve("what to do in Maasai mara", top_n_vector=25, top_k_final=5)
    retriever.setup_model()
    final_result = retriever.query_response("What to do in Maasai Mara")
    print(final_result)