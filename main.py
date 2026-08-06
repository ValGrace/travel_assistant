from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from langchain_community.vectorstores import Chroma
import uvicorn
from pydantic import BaseModel
from RAG.retriever import RetrieveContext
from RAG.embeddings import SentenceTransformerEmbeddings

templates = Jinja2Templates(directory="templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> LIFESPAN STARTING")
    embedding_fn = SentenceTransformerEmbeddings('all-mpnet-base-v2')
    vector_store = Chroma(
        collection_name="kenyan-tourism-collection",
        # embedding_function=embedding_fn,
        persist_directory="data/chroma_db",
    )
    app.state.retriever = RetrieveContext(vector_store=vector_store)
    app.state.retriever.setup_model()
    print(">>> LIFESPAN READY, retriever set:", app.state.retriever)
    yield

app = FastAPI(title="Kenyan tourism intelligence API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def index():
    return {"status": "App is running"}

@app.post("/query")
async def query_files(payload: QueryRequest):
    return app.state.retriever.query_response(payload.question)
   


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "name": "Grace Anyango"
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)