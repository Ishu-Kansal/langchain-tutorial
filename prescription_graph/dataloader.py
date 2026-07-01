import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter

drug_client = chromadb.Client()
patient_client = chromadb.Client()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400, separators=["\n\n", "\n", " ", ""])

drugInfos = drug_client.create_collection(name="drug_info")
patientInfos = patient_client.create_collection(name="patient_history")
embedding_func = embedding_functions.DefaultEmbeddingFunction()


DRUG_LOAD_LIST = [
    {"key": "proair hfa", "path": "./data/drugs/proair_hfa.txt"},
]

def _initialize_and_load_data():
    for item in DRUG_LOAD_LIST:
        if os.path.exists(item["path"]):
            with open(item["path"], "r", encoding="utf-8") as f:
                text = f.read()
            raw_chunks = text_splitter.split_text(text)
            chunks = []
            for chunk in raw_chunks:
                context_header = f"DOCUMENT: {item['key'].upper()} Interactions, Warnings, and Contraindications.\nCONTENT:\n"
                chunks.append(context_header + chunk)
            ids = [f"{item['key']}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"drug_name": item["key"].lower()} for _ in chunks]
            drugInfos.add(documents=chunks, metadatas=metadatas, ids=ids)
            print(f"Loaded {item['key']} reference data into memory.")
        else:
            print(f"Could not find drug file at {item['path']}")
            
_initialize_and_load_data()