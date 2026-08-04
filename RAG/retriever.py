from sentence_transformers import CrossEncoder
from langchain_community.vectorstores import Chroma
# from RAG.embeddings import SentenceTransformerEmbeddings
import google.genai as genai
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

def _extract_json(raw_text: str) -> dict:
    """Strip accidental code fences and parse the model's JSON response.
    Falls back to a minimal structure (with the raw text as the intro)
    if the model didn't return valid JSON, so the frontend never breaks.
    """
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
 
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = {}
 
    return {
        "intro": parsed.get("intro") or (raw_text if not parsed else ""),
        "missing_info": parsed.get("missing_info", []) or [],
        "highlights": parsed.get("highlights", []) or [],
        "itinerary": parsed.get("itinerary", []) or [],
        "follow_up_questions": parsed.get("follow_up_questions", []) or [],
    }

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
        You are a travel assistant knowlegeable about hotels, destinations, safari trips, coastal vacations, and travel planning in Kenya. If the answer is not in the context, say so in "missing_info" instead of guessing.
         
        Context: {context}

        Lets plan your next trip: {tourism_query}

         Respond with ONLY a valid JSON object — no markdown, no code fences, no commentary before or after — matching exactly this schema:
 
        {{
          "intro": "2-3 sentence plain-English overview of what you found and any caveats",
          "missing_info": ["short phrase for each thing not covered by the context, e.g. 'coastal pricing'"],
          "highlights": [
            {{"title": "Experience or place name", "description": "1-2 sentence plain-English description"}}
          ],
          "itinerary": [
            {{
              "day": 1,
              "title": "Short day title",
              "activity": "1-3 sentence description of the day's plan",
              "accommodation_options": ["Hotel or lodge name", "..."],
              "cost": "price from context, or 'Not available in context'"
            }}
          ],
          "follow_up_questions": ["question 1", "question 2", "question 3"]
        }}
 
        Rules:
        - itinerary should have one entry per day of the trip requested.
        - accommodation_options should only include names that appear in the context.
        - Keep highlights to the most relevant 3-5 experiences.
        - follow_up_questions should have exactly 3 questions that narrow down the plan. 

        
          
         """
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_template
            )
        return _extract_json(response.text)



# if __name__ == "__main__":
#     embedding_fn = SentenceTransformerEmbeddings('all-mpnet-base-v2')
#     vector_store = Chroma(
#     collection_name="kenyan-tourism-collection",
#     embedding_function=embedding_fn,
#     persist_directory="data/chroma_db"
#     )

#     retriever = RetrieveContext(vector_store=vector_store)
    # results = retriever.retrieve("what to do in Maasai mara", top_n_vector=25, top_k_final=5)
    # retriever.setup_model()
    # final_result = retriever.query_response("What to do in Maasai Mara")
    # print(final_result)

    # Instructions:
    #         1. Search for relevant hotels, destinations, prices, amenities, locations, safari trips in the context
    #         2. Provide the most suitable recommendations.
    #         3. Explain why the recommendation briefly.
    #         4. Ask the user follow up questions to generate the most accurate answer.
    #         5. Rewrite the returned context into plain english and natural language conversion.
    #         6. For each returned context, generate a day by day itenary plan with where the accomodations and activities and include the cost. Plans balance nearby must-see highlights with hidden gems.