from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import shutil, os, time
from ingestion import text_splitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate


class TravelAssistant:
    def __init__(self, data_path='', persist_directory='./chroma_db'):
        self.data_path = data_path
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.qa_chain = None

    def create_vectorstore(self, chunks):
        """ Create vector database from chunks. """
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-miniLM-L6-v2"
        )

        self.vectorstore = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            persist_directory=self.persist_directory
        )
    def load_vectorstore(self):
        """ Load existing vector database."""
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=embeddings
        )

    def build_prompt(self):
        template = """ 
        You are a travel assistant knowlegeable about hotels, destinations, safari trips, coastal vacations, and travel planning in Kenya. If the answer is not in the context, say you don't have enough information - do not guess
         
        Context: {context}

        Lets plan your next trip: {question}

        Instructions:
        1. Search for relevant hotels, destinations, prices, amenities, locations, safari trips in the context
        2. Provide the most suitable recommendation.
        3. Explain why the recommendation briefly
          
         """
        prompt = PromptTemplate(
            template=template,
            input_variables=['context', 'question']
        )

        print('Initializing Gemini model...')
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.3,
            google_api_key=os.get_env('GOOGLE_API_KEY')
        )

        