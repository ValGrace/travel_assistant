from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document
import re

class TextChunks:
    def __init__(self, data_paths):
        if isinstance(data_paths, str):
            self.data_paths = [data_paths]
        else:
            self.data_paths = data_paths

# recursive chunking
    def load_and_chunk_data(self):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100,
            separators=["\n\n"]
        )
        all_chunks = []

        for path in self.data_paths:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = text_splitter.split_text(text)
            print(f"Created {len(chunks)} chunks from document")
            all_chunks.extend(chunks)

        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

